import re
from django import forms
from django.views.generic.edit import FormView
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.safestring import mark_safe
from decimal import Decimal


WALLET_RE = re.compile(r"^0x[a-fA-F0-9]{30,40}$")


class CreateTransactionForm(forms.Form):

    amount = forms.DecimalField(max_digits=16, decimal_places=12, help_text="The amount of ETH you want to send")

    recipient = forms.CharField(max_length=300, label="Recipient", help_text="Which address are you sending to")

    fee = forms.DecimalField(
        max_digits=16, decimal_places=12, help_text="The fee in ETH to pay to miners to have your transaction accepted"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        return super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        fee = cleaned_data.get("fee")
        amount = cleaned_data.get("amount")
        if fee is not None and amount is not None and (fee + amount) > self.user.balance:
            raise forms.ValidationError("The total of the amount and the fee is higher than your wallet balance")
        return cleaned_data

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount > self.user.balance:
            raise forms.ValidationError("You don't have enough ETH in your wallet to send that amount")
        return amount

    def clean_fee(self):
        fee = self.cleaned_data["fee"]
        if fee > self.user.balance:
            raise forms.ValidationError("You don't have enough ETH in your wallet to use that as the fee")
        return fee

    def clean_recipient(self):
        recipient = self.cleaned_data["recipient"]
        if not WALLET_RE.match(recipient):
            raise forms.ValidationError("Please enter a valid address")
        if recipient == self.user.wallet.address:
            raise forms.ValidationError("That is your own address, it seems a bit of a waste to send to yourself!")
        return recipient


class TxDisplay:
    """
    Simple wrapper class to do some formatting on Transaction objects to make
    them a little bit nicer for display
    """

    def __init__(self, tx, user):
        self.tx = tx
        self.user = user

    def formatted_amount(self):
        return Decimal(self.tx.quantity) / (10 ** 18)

    def short_hash(self):
        return self.tx.txhash[:16]

    def button_class(self):
        return {"CONFIRMED": "success", "PENDING": "warning", "CONFIRMING": "info"}.get(self.tx.status, "secondary")

    def short_recipient(self):
        return self.tx.recipient[:16]

    def incoming(self):
        return self.user.wallet.address == self.tx.recipient


class SinglePage(FormView):

    template_name = "core/singlepage.html"
    form_class = CreateTransactionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx["transactions"] = [TxDisplay(tx, self.request.user) for tx in self.request.user.get_transactions()]
        return ctx

    def form_valid(self, form):
        amount = int(form.cleaned_data["amount"] * (10 ** 18))
        fee = int(form.cleaned_data["fee"] * (10 ** 18))
        transaction = self.request.user.send(form.cleaned_data["recipient"], amount, fee)

        tx_url = "https://ropsten.etherscan.io/tx/%s" % transaction.txhash
        message = "Your transaction was successfully created with the ID <a href='%s'>%s</a>" % (
            tx_url,
            transaction.txhash,
        )
        messages.add_message(self.request, messages.SUCCESS, mark_safe(message))

        return redirect("core:singlepage")

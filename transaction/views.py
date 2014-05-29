from base.views import BaseView
from transaction.models import Transaction
from transactionreal.models import TransactionReal
from transaction.forms import NewTransactionForm, EditTransactionForm
from userprofile.models import UserProfile

from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView

from itertools import chain

import logging
logger = logging.getLogger(__name__)

  
class TransactionView(BaseView):
  template_name = "transaction/index.html"
  context_object_name = "transaction"
  
  def get_context_data(self, **kwargs):
    context = super(TransactionView, self).get_context_data(**kwargs)
    transactions = Transaction.objects.order_by('date')[:50].reverse()
    context['latest_transactions_list'] = transactions
    return context
    
    
class MyTransactionView(BaseView):
  template_name = "transaction/mytransactions.html"
  context_object_name = "my transactions"
  
  def getActiveMenu(self):
    return 'shares'
  
  def getBuyerTransactions(self, buyerId):
    transactions = Transaction.objects.filter(buyer__id=buyerId).order_by("date")
    for transaction in transactions:
      transaction.amountPerPerson = '%.2f' % (transaction.amount)
      transaction.amountPerPersonFloat = transaction.amount
    return transactions
    
  def getConsumerTransactions(self, consumerId):
    transactions = Transaction.objects.filter(consumers__id=consumerId).order_by("date")
    for transaction in transactions:
      transaction.amountPerPerson = '%.2f' % (-1*transaction.amount/transaction.consumers.count())
      transaction.amountPerPersonFloat = (-1*transaction.amount/transaction.consumers.count())
    return transactions
    
  def getSentTransactionsReal(self, senderId):
    transactions = TransactionReal.objects.filter(sender__id=senderId).order_by("date")
    for transaction in transactions:
      transaction.amountPerPerson = '%.2f' % (-1*transaction.amount)
      transaction.amountPerPersonFloat = (-1*transaction.amount)
    return transactions
    
  def getReceivedTransactionsReal(self, receiverId):
    transactions = TransactionReal.objects.filter(receiver__id=receiverId).order_by("date")
    for transaction in transactions:
      transaction.amountPerPerson = '%.2f' % (1*transaction.amount)
      transaction.amountPerPersonFloat = (1*transaction.amount)
    return transactions
  
  def getNumberOfBuyerTransactions(self, buyerId):
    transactions = Transaction.objects.filter(buyer__id=buyerId)
    return len(transactions)
  
  def get_context_data(self, **kwargs):
    logger.debug("start")
    # Call the base implementation first to get a context
    context = super(MyTransactionView, self).get_context_data(**kwargs)
    userProfile = UserProfile.objects.get(user=self.request.user)
    buyerTransactions = self.getBuyerTransactions(userProfile.id)
    consumerTransactions = self.getConsumerTransactions(userProfile.id)
    transactionsAll = list(chain(buyerTransactions, consumerTransactions))
    
    transactionsAllSorted = sorted(transactionsAll, key=lambda instance: instance.date, reverse=True)[:10]
    
#     sentTransactions = self.getSentTransactionsReal(userProfile.id)
#     receivedTransactions = self.getReceivedTransactionsReal(userProfile.id)
#     transactionsRealAll = list(chain(sentTransactions, receivedTransactions))
#     transactionsRealAllSorted = sorted(transactionsRealAll, key=lambda instance: instance.date, reverse=True)
    
#     context['buyer_transactions'] = self.getBuyerTransactions(userProfile.id)
#     context['consumer_transactions'] = self.getConsumerTransactions(userProfile.id)
#     context['transactionsRealAll'] = transactionsRealAllSorted
    context['transactionsAll'] = transactionsAllSorted
    if int(context['tableView']) == 0:
      context['tableView'] = False
    return context


class SelectGroupTransactionView(BaseView):
  template_name = "transaction/newselectgroup.html"
  context_object_name = "select transaction group"
  
  def get_context_data(self, **kwargs):    
    context = super(SelectGroupTransactionView, self).get_context_data(**kwargs)
    
    userProfile = UserProfile.objects.get(user=self.request.user)
    groupaccounts = userProfile.groupAccounts.all
    context['groupaccounts'] = groupaccounts
    
    return context


class NewTransactionView(FormView, BaseView):
  template_name = 'transaction/new.html'
  form_class = NewTransactionForm
  success_url = '/transaction/new/success/'
  
  def getActiveMenu(self):
    return 'shares'
   
  def getGroupAccountId(self):
    if 'groupAccountId' in self.kwargs:
      return self.kwargs['groupAccountId']
    else:
      logger.debug(self.request.user.id)
      user = UserProfile.objects.get(user=self.request.user)
      if user.groupAccounts.count():
        return user.groupAccounts.all()[0].id
      else:
        return 0
    
  def get_form(self, form_class):
    return NewTransactionForm(self.getGroupAccountId(), self.request.user, **self.get_form_kwargs())   
    
  def form_valid(self, form):
    logger.debug('NewTransactionView::form_valid()')
    super(NewTransactionView, self).form_valid(form)
    form.save()
    return HttpResponseRedirect( '/')
  
  def form_invalid(self, form):
    logger.debug('NewTransactionView::form_invalid()')
    groupAccount = form.cleaned_data['groupAccount'] 
    logger.debug('groupAccount.id = ' + str(groupAccount.id))
    logger.debug('getGroupAccountId = ' + str(self.getGroupAccountId()))
    if int(groupAccount.id) != int(self.getGroupAccountId()): 
      return HttpResponseRedirect( '/transactions/new/' + str(groupAccount.id))
    else:
      return super(NewTransactionView, self).form_invalid(form)
  
  def get_context_data(self, **kwargs):
    logger.debug('NewTransactionView::get_context_data() - groupAccountId: ' + str(self.getGroupAccountId()))
    context = super(NewTransactionView, self).get_context_data(**kwargs)
    
    if (self.getGroupAccountId()):
      form = NewTransactionForm(self.getGroupAccountId(), self.request.user, **self.get_form_kwargs())
      context['form'] = form
      context['nogroup'] = False
    else:
      context['nogroup'] = True
    
    return context


class EditTransactionView(FormView, BaseView):
  template_name = 'transaction/edit.html'
  form_class = EditTransactionForm
  success_url = '/transactions/0'
  
  def getActiveMenu(self):
    return 'shares'
   
  def get_form(self, form_class):
    pk = self.kwargs['pk']
    transaction = Transaction.objects.get(pk=pk)
    return EditTransactionForm(self.kwargs['pk'], self.request.user, instance=transaction, **self.get_form_kwargs())   

#   def get_initial(self):
#     return { 'consumers': UserProfile.objects.filter(groupAccounts=2)}

  def form_valid(self, form):
    logger.debug('EditTransactionView::form_valid()')
    super(EditTransactionView, self).form_valid(form)
    form.save()
    return HttpResponseRedirect( '/transactions/0' )
  
  def get_context_data(self, **kwargs):
    logger.debug('EditTransactionView::get_context_data()')
    context = super(EditTransactionView, self).get_context_data(**kwargs)
    transaction = Transaction.objects.get(pk=self.kwargs['pk'])
    form = EditTransactionForm(self.kwargs['pk'], self.request.user, instance=transaction, **self.get_form_kwargs())
    context['form'] = form
    
    return context


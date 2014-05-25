# Create your views here.
from base.views import BaseView
from transactionreal.forms import NewRealTransactionForm
from transactionreal.models import TransactionReal
from userprofile.models import UserProfile

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView

from itertools import chain

import logging
logger = logging.getLogger(__name__)


class MyRealTransactionView(BaseView):
  template_name = "transactionreal/mytransactionsreal.html"
  context_object_name = "my real transactions"
  
  def getActiveMenu(self):
    return 'transactions'
    
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
    
  def getBalance(self, groupAccountId, userProfileId):
    senderRealTransactions = TransactionReal.objects.filter(groupAccount__id=groupAccountId, sender__id=userProfileId)
    receiverRealTransactions = TransactionReal.objects.filter(groupAccount__id=groupAccountId, receiver__id=userProfileId)
    
    totalBought = 0.0
    totalConsumed = 0.0
    totalSent = 0.0
    totalReceived = 0.0
      
    for transaction in senderRealTransactions:
      totalSent += transaction.amount
      
    for transaction in receiverRealTransactions:
      totalReceived += transaction.amount
      
    balance = (totalBought + totalSent - totalConsumed - totalReceived)
    return balance
  
  def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
    context = super(MyRealTransactionView, self).get_context_data(**kwargs)
    userProfile = UserProfile.objects.get(user=self.request.user)
     
    sentTransactions = self.getSentTransactionsReal(userProfile.id)
    receivedTransactions = self.getReceivedTransactionsReal(userProfile.id)
    transactionsRealAll = list(chain(sentTransactions, receivedTransactions))
    transactionsRealAllSorted = sorted(transactionsRealAll, key=lambda instance: instance.date, reverse=True)
    
    if int(context['tableView']) == 0:
      context['tableView'] = False
    
    context['transactionsRealAll'] = transactionsRealAllSorted
    return context# Create your views here.


class SelectGroupRealTransactionView(BaseView):
  template_name = "transactionreal/newselectgroup.html"
  context_object_name = "select transaction group"
  
  def get_context_data(self, **kwargs):    
    context = super(SelectGroupRealTransactionView, self).get_context_data(**kwargs)
    userProfile = UserProfile.objects.get(user=self.request.user)
    groupaccounts = userProfile.groupAccounts.all
    context['groupaccounts'] = groupaccounts
    context['transactionssection'] = True
    return context


class NewRealTransactionView(FormView, BaseView):
  template_name = 'transactionreal/new.html'
  form_class = NewRealTransactionForm
  success_url = '/transactionreal/new/success/'
  
  def getActiveMenu(self):
    return 'transactions'
   
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
    logger.debug('get_form()')
    return NewRealTransactionForm(self.getGroupAccountId(), self.request.user, **self.get_form_kwargs())   
    
  def form_valid(self, form):
    logger.debug('form_valid()')
    super(NewRealTransactionView, self).form_valid(form)
    
    form.save()
    
    return HttpResponseRedirect( '/')
  
  def form_invalid(self, form):
    logger.debug('form_invalid()')
    groupAccount = form.cleaned_data['groupAccount']  
    super(NewRealTransactionView, self).form_invalid(form)
    
    return HttpResponseRedirect( '/transactionsreal/new/' + str(groupAccount.id))
  
  def get_context_data(self, **kwargs):
    logger.debug('NewRealTransactionView::get_context_data() - groupAccountId: ' + str(self.getGroupAccountId()))
    context = super(NewRealTransactionView, self).get_context_data(**kwargs)
    
    if (self.getGroupAccountId()):
      form = NewRealTransactionForm(self.getGroupAccountId(), self.request.user)
      context['form'] = form
      context['nogroup'] = False
    else:
      context['nogroup'] = True
    return context

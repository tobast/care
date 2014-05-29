from django import forms
from django.contrib.auth.models import User

from groupaccount.models import GroupAccount
from userprofile.models import UserProfile

class EditUserProfileForm(forms.ModelForm):
  
  def __init__(self, user, *args, **kwargs):
    super(EditUserProfileForm, self).__init__(*args, **kwargs)
    
    userProfile = UserProfile.objects.get(user=user)
    self.fields['user'] = forms.ModelChoiceField(widget=forms.HiddenInput, 
                                                 queryset=User.objects.filter(id=user.id), 
                                                 empty_label=None)
    
    self.fields['displayname'] = forms.CharField(max_length=100, label='Display name')
#     self.fields['displayname'].widget.attrs['readonly'] = True
    
    self.fields['groupAccounts'] = forms.ModelMultipleChoiceField(widget=forms.MultipleHiddenInput, 
                                                                  queryset=userProfile.groupAccounts.all(), 
                                                                  label='Groups')
  
  class Meta:
    model = UserProfile

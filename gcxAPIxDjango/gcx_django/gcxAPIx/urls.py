from .server import *
from .login_requests import *
from .plagiarism import *
from .downloads import *
from .documents import *
from .userAccount import *
from .payments import *
from django.urls import path, include, re_path, reverse_lazy
from rest_framework import routers
from django.views.generic.base import RedirectView


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.


urlpatterns = [
    #path('', include(router.urls)),
    path('status/', signUpUser1),
    path('activateUserAccount/', activateUserAccount),
    path('getUserProfileContents/', getUserProfileContents),
    path('submitEDocument/', submitEDocument),
    path('helpCentre/', helpCentre),
    #path('getHelpFAQsListing/', getHelpFAQsListing),
    path('userWizard/', userWizard),
    path('getPreferredLangByProfileID/', getPreferredLangByProfileID),
    path('addReportedRule/', addReportedRule),
    path('addCompTexttoDB/', addCompTexttoDB),
    path('getuserfilters/', getuserfilters),
    path('getuserfiltersAccount/', getuserfiltersAccount),
    path('addIgnoreWord/', addIgnoreWord),
    path('ignoreWordList/', ignoreWordList),
    path('test/', testing),
    path('userLogin/', userLogin.as_view()),
    path('signupFormProcesses/', signupFormProcesses),
    path('signupinGoogleTesting/', GoogleLogin.as_view()),
    path('signupinFacebookTesting/', FacebookLogin.as_view()),
    path('logoutuser/', logoutuser),
    path('checkPlagiarism_break_data_grm/', checkPlagiarism_break_data_grm),
    path('checkPlagiarism_grm_response/', checkPlagiarism_grm_response),
    path('getPlagCompareText/', getPlagCompareText),
    path('downloadPDFByDocId/<doc_id>', downloadPDFByDocId),
    path('downloadDOCByDocId/<doc_id>', downloadDOCByDocId),
    path('downloadFromDrive/', downloadFromDrive),
    path('getDocumentsListing/', getDocumentsListing),
    path('getDocContentsPublic/', getDocContentsPublic),
    path('getDocDataByProfileDocID/', getDocDataByProfileDocID),
    path('getNewDocIDbyProfileID/', getNewDocIDbyProfileID),
    path('getNewDocIDForGuestByContents/', getNewDocIDForGuestByContents),
    path('getNewDocIDbyProfileIDFileContents/', getNewDocIDbyProfileIDFileContents),
    path('getNewDocIDbyProfileIDContents/', getNewDocIDbyProfileIDContents),
    path('getNewDocIDbyProfileIDContentsbyURL/', getNewDocIDbyProfileIDContentsbyURL),
    path('getNewDocIDbyProfileIDusingFileName/', getNewDocIDbyProfileIDusingFileName),
    path('deleteDocumentByID/', deleteDocumentByID),
    path('saveDocbyProfileIDusingDocID/', saveDocbyProfileIDusingDocID),
    path('getchunkslicing/', getchunkslicing),
    path('createchunks/', createchunks),
    path('getAbbreviations', getAbbreviations),
    path('accountConfirm/', accountConfirm),
    path('deleteUserByProfileID/', deleteUserByProfileID),
    path('resetPassword/', resetPassword),
    path('updateUserForgotPassword/', updateUserForgotPassword),
    path('updateUserPassword/', updateUserPassword),
    path('updateProfileContents/', updateProfileContents),
    path('updateUserLanguage/', updateUserLanguage),
    path('updateuserfiltersAccount/', updateuserfiltersAccount),
    path('updateuserfilters/', updateuserfilters),
    path('submitEForm/', submitEForm),
    path('submitSupportForm/', submitSupportForm),
    path('checkSubscriptionStatus/', getSubscriptionStatus),
    path('listPackages/', getProductsDetails),
    path('getCheckoutURL/', createCheckoutSession),
    path('subscriptionDetails/', subscriptionDetails),
    path('getBillingHistory/', getBillingHistory),
    path('cancelSubscription/', cancelSubscription),
    path('getinvoice/', generate_invoice),
    path('webhook/ipnconfirm/', ipnConfirm),
    #path('', include('rest_framework.urls', namespace='rest_framework')),
    #re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

]
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

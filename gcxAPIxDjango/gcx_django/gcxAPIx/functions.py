import json
import base64
import sendgrid
from sendgrid.helpers.mail import *
from .factory import getConnection


###########################################
# ADDED BY HASEEB def sendAttachmentEmailPdf
###########################################

def sendAttachmentEmailPdf(from_address, email_to, email_sub, email_body, path):
    # pip install sendgrid
    # using SendGrid's Python Library
    # https://github.com/sendgrid/sendgrid-python

    # Encode contents of file as Base 64
    # file_path = "/var/www/GCX/docx/xyz.docx"

    with open(path, 'rb') as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.content = encoded
    attachment.type = "application/pdf"
    attachment.filename = path.split('/')[-1]
    attachment.disposition = "attachment"
    attachment.content_id = "GCX-Document"
    SENDGRID_API_KEY = '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'
    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
    from_email = Email(from_address, 'GrammarIn')
    to_email = Email(email_to)
    subject = email_sub
    content = Content("text/html", email_body)
    mail = Mail(from_email, subject, to_email, content)
    mail.add_attachment(attachment)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.body)
    print(response.headers)
    return response.status_code


def sendAttachmentEmailWord(from_address, email_to, email_sub, email_body, path):
    # pip install sendgrid
    # using SendGrid's Python Library
    # https://github.com/sendgrid/sendgrid-python

    # Encode contents of file as Base 64
    # file_path = "/var/www/GCX/docx/xyz.docx"

    with open(path, 'rb') as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.content = encoded
    attachment.type = "application/docx"
    attachment.filename = path.split('/')[-1]
    attachment.disposition = "attachment"
    attachment.content_id = "GCX-Document"
    SENDGRID_API_KEY = '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'
    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
    from_email = Email(from_address, 'GrammarIn')
    to_email = Email(email_to)
    subject = email_sub
    content = Content("text/html", email_body)
    mail = Mail(from_email, subject, to_email, content)
    mail.add_attachment(attachment)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.body)
    print(response.headers)
    return response.status_code


def sendEmail(from_address, to_address, subject, message):
    # pip install sendgrid
    # using SendGrid's Python Library
    # https://github.com/sendgrid/sendgrid-python

    SENDGRID_API_KEY = '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'
    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
    from_email = Email(from_address, 'GrammarIn')
    to_email = Email(to_address)
    subject = subject
    content = Content("text/html", message)

    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.body)
    print(response.headers)
    return response.status_code


def initializeFilters(user_id, doc_id, status):
    conn = getConnection()
    curr = conn.cursor()
    row = []
    if status == 'premium':
        filters = {
            "article_algo": True,
            "formal_tones": True,
            "sva_auxiliary": True,
            "to_inf_simple": True,
            "determiner_algo": True,
            "sequence_modals": True,
            "to_inf_add_list": True,
            "verb_verb_agrmt": True,
            "contracted_forms": True,
            "oxford_comma_add": True,
            "sign_replacement": True,
            "modals_verb_agrmt": True,
            "sva_non_auxiliary": True,
            "active_passive_aux": True,
            "auxiliary_addition": True,
            "formal_tones_inter": True,
            "punctuation_checker": True,
            "active_passive_modals": True,
            "preposition_formality": True,
            "verb_removal_solution": True,
            "capitalization_checker": True,
            "double_negative_removal": False,
            "contracted_forms_cons_rem": True,
            "lt_style": True,
            "lt_grammar": True,
            "lt_wikipedia": True,
            "lt_semantics": True,
            "lt_typography": True,
            "lt_punctuation": True,
            "lt_compounding": True,
            "lt_collocation": True,
            "lt_plain_english": True,
            # "lt_text_analysis":True,
            "lt_miscellaneous": True,
            "lt_possible_typo": True,
            "lt_capitalization": True,
            "lt_academic_writing": True,
            "lt_upper_lower_case": True,
            "lt_creative_writing": True,
            "lt_redundant_phrases": True,
            "lt_nonstandard_phrases": True,
            "lt_commonly_confused_words": True,
        }
    elif status == 'aftersignup':
        filters = {
            "article_algo": True,
            "formal_tones": True,
            "sva_auxiliary": True,
            "to_inf_simple": False,
            "determiner_algo": False,
            "sequence_modals": False,
            "to_inf_add_list": False,
            "verb_verb_agrmt": True,
            "contracted_forms": True,
            "oxford_comma_add": False,
            "sign_replacement": True,
            "modals_verb_agrmt": True,
            "sva_non_auxiliary": True,
            "active_passive_aux": False,
            "auxiliary_addition": True,
            "formal_tones_inter": False,
            "punctuation_checker": True,
            "active_passive_modals": False,
            "preposition_formality": False,
            "verb_removal_solution": True,
            "capitalization_checker": True,
            "double_negative_removal": True,
            "contracted_forms_cons_rem": True,
            "lt_style": True,
            "lt_grammar": True,
            "lt_wikipedia": True,
            "lt_semantics": True,
            "lt_typography": True,
            "lt_punctuation": True,
            "lt_compounding": True,
            "lt_collocation": True,
            "lt_plain_english": True,
            # "lt_text_analysis":True,
            "lt_miscellaneous": True,
            "lt_possible_typo": True,
            "lt_capitalization": True,
            "lt_academic_writing": True,
            "lt_upper_lower_case": True,
            "lt_creative_writing": True,
            "lt_redundant_phrases": True,
            "lt_nonstandard_phrases": True,
            "lt_commonly_confused_words": True,
        }
    elif status == 'beforesignup':
        filters = {
            "article_algo": False,
            "formal_tones": False,
            "sva_auxiliary": False,
            "to_inf_simple": False,
            "determiner_algo": False,
            "sequence_modals": False,
            "to_inf_add_list": False,
            "verb_verb_agrmt": False,
            "contracted_forms": False,
            "oxford_comma_add": False,
            "sign_replacement": False,
            "modals_verb_agrmt": False,
            "sva_non_auxiliary": False,
            "active_passive_aux": False,
            "auxiliary_addition": False,
            "formal_tones_inter": False,
            "punctuation_checker": False,
            "active_passive_modals": False,
            "preposition_formality": False,
            "verb_removal_solution": False,
            "capitalization_checker": False,
            "double_negative_removal": False,
            "contracted_forms_cons_rem": False,
            "lt_style": False,
            "lt_grammar": False,
            "lt_wikipedia": False,
            "lt_semantics": False,
            "lt_typography": False,
            "lt_punctuation": False,
            "lt_compounding": False,
            "lt_collocation": False,
            "lt_plain_english": False,
            # "lt_text_analysis":False,
            "lt_miscellaneous": False,
            "lt_possible_typo": False,
            "lt_capitalization": False,
            "lt_academic_writing": False,
            "lt_upper_lower_case": False,
            "lt_creative_writing": False,
            "lt_redundant_phrases": False,
            "lt_nonstandard_phrases": False,
            "lt_commonly_confused_words": False,
        }
    else:
        filters = {}
    query = ("INSERT INTO user_filters(user_id, doc_id, filters) VALUES('%s', '%s', '%s') RETURNING filters;" % (
        user_id, doc_id, json.dumps(filters)))
    try:
        curr.execute(query)
        conn.commit()
        row = curr.fetchone()
    except Exception as e:
        print("Error Happend in execution.", e)
        conn.rollback()
    finally:
        conn.close()
    return row
def prepareOutputWeb(var, language):

    FinalOutput = {}
    Software_Details = {}
    Software_Details['name'] = 'GrammarIn'
    Software_Details['version'] = '1.01'
    Software_Details['buildDate'] = '2017-11-04 00:00:00'
    Software_Details['apiVersion'] = '1.01'
    Software_Details['status'] = 'stable'
    Language_Details = {}
    Language_Details['name'] = ''
    Language_Details['code'] = language

    FinalOutput['software'] = Software_Details
    FinalOutput['language'] = Language_Details

    MatchesOutput = []

    for i in var:
        if type(i) in (list, tuple, dict, set):
            #var_dump(i)
            abc = 1
        else:
            if isinstance(var, dict):
                #print(i, ': (', var[i].__class__.__name__, ') ', var[i])
                abc = 1
            else:
                Match = {}
                Match['message'] = i.message # msg
                Match['shortMessage'] = ""
                Match['offset'] = i.offset
                Match['length'] = i.errorlength

                Match['fromy'] = i.fromy
                Match['fromx'] = i.fromx
                Match['toy'] = i.toy
                Match['tox'] = i.tox

                Match_Replacement = i.replacements
                Replacement_Array = []

                for j in Match_Replacement:
                    Replacement_Array2 = {}
                    Replacement_Array2['value'] = j
                    Replacement_Array.append(Replacement_Array2)

                Match['replacements'] = Replacement_Array

                Match_Context = i.contextoffset

                Context_Array = {}
                Context_Array['text'] = i.context
                Context_Array['offset'] = i.offset
                Context_Array['length'] = i.errorlength
                Match['context'] = Context_Array

                Match_Rule_URLs = ''
                Match_Rule_Category = i.category

                Match_Rule = {}
                Match_Rule['id'] = i.ruleId
                Match_Rule['subId'] = ''
                Match_Rule['description'] = ''
                Match_Rule['urls'] = Match_Rule_URLs
                Match_Rule['issueType'] = i.locqualityissuetype
                Match_Rule['category'] = Match_Rule_Category

                Category_Array = {}
                Category_Array['id'] = ''
                Category_Array['name'] = i.category
                Match_Rule['category'] = Category_Array

                Match['rule'] = Match_Rule

                MatchesOutput.append(Match)

    FinalOutput['matches'] = MatchesOutput
    return FinalOutput

import os
from io import BytesIO
from datetime import date

from reportlab.lib import enums
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, ListFlowable, \
    KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor, black, blue

from django.core.files import File
from django.conf import settings

from wildlifelicensing.apps.main.helpers import render_user_name

from ledger.accounts.models import Document

BW_DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'wildlifelicensing', 'static', 'wl', 'img',
                                'bw_dpaw_header_logo.png')

COLOUR_DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'wildlifelicensing', 'static', 'wl', 'img',
                                       'colour_dpaw_header_logo.png')

PAGE_WIDTH, PAGE_HEIGHT = A4

DEFAULT_FONTNAME = 'Helvetica'
BOLD_FONTNAME = 'Helvetica-Bold'

VERY_LARGE_FONTSIZE = 14
LARGE_FONTSIZE = 12
MEDIUM_FONTSIZE = 10
SMALL_FONTSIZE = 8

PARAGRAPH_BOTTOM_MARGIN = 5

SECTION_BUFFER_HEIGHT = 10

DATE_FORMAT = '%d/%m/%Y'

HEADER_MARGIN = 10
HEADER_SMALL_BUFFER = 3

PAGE_MARGIN = 20
PAGE_TOP_MARGIN = 200

LETTER_HEADER_MARGIN = 30
LETTER_PAGE_MARGIN = 60
LETTER_IMAGE_WIDTH = 242
LETTER_IMAGE_HEIGHT = 55
LETTER_HEADER_SMALL_BUFFER = 5
LETTER_ADDRESS_BUFFER_HEIGHT = 40


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='InfoTitleLargeCenter', fontName=BOLD_FONTNAME, fontSize=LARGE_FONTSIZE,
                          spaceAfter=PARAGRAPH_BOTTOM_MARGIN, alignment=enums.TA_CENTER))
styles.add(ParagraphStyle(name='InfoTitleVeryLargeCenter', fontName=BOLD_FONTNAME, fontSize=VERY_LARGE_FONTSIZE,
                          spaceAfter=PARAGRAPH_BOTTOM_MARGIN * 2, alignment=enums.TA_CENTER))
styles.add(ParagraphStyle(name='InfoTitleLargeLeft', fontName=BOLD_FONTNAME, fontSize=LARGE_FONTSIZE,
                          spaceAfter=PARAGRAPH_BOTTOM_MARGIN, alignment=enums.TA_LEFT,
                          leftIndent=PAGE_WIDTH / 10, rightIndent=PAGE_WIDTH / 10))
styles.add(ParagraphStyle(name='InfoTitleLargeRight', fontName=BOLD_FONTNAME, fontSize=LARGE_FONTSIZE,
                          spaceAfter=PARAGRAPH_BOTTOM_MARGIN, alignment=enums.TA_RIGHT,
                          rightIndent=PAGE_WIDTH / 10))
styles.add(ParagraphStyle(name='BoldLeft', fontName=BOLD_FONTNAME, fontSize=MEDIUM_FONTSIZE, alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='BoldRight', fontName=BOLD_FONTNAME, fontSize=MEDIUM_FONTSIZE, alignment=enums.TA_RIGHT))
styles.add(ParagraphStyle(name='Center', alignment=enums.TA_CENTER))
styles.add(ParagraphStyle(name='Left', alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='Right', alignment=enums.TA_RIGHT))


def _create_licence_header(canvas, doc, draw_page_number=True):
    canvas.setFont(BOLD_FONTNAME, LARGE_FONTSIZE)

    current_y = PAGE_HEIGHT - HEADER_MARGIN

    canvas.drawCentredString(PAGE_WIDTH / 2, current_y - LARGE_FONTSIZE, 'DEPARTMENT OF PARKS AND WILDLIFE')

    current_y -= 30

    dpaw_header_logo = ImageReader(BW_DPAW_HEADER_LOGO)
    dpaw_header_logo_size = dpaw_header_logo.getSize()
    canvas.drawImage(dpaw_header_logo, HEADER_MARGIN, current_y - dpaw_header_logo_size[1])

    current_x = HEADER_MARGIN + dpaw_header_logo_size[0] + 5

    canvas.setFont(DEFAULT_FONTNAME, SMALL_FONTSIZE)

    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER), 'Enquiries:')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2, 'Telephone:')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3, 'Facsimile:')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4, 'Web Site:')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 5, 'Correspondance:')

    current_x += 80

    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER),
                      '17 DICK PERRY AVE, KENSINGTON, WESTERN AUSTRALIA')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2, '08 9219 9000')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3, '08 9219 8242')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4, doc.site_url)

    canvas.setFont(BOLD_FONTNAME, SMALL_FONTSIZE)
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 5, 'Locked Bag 30')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 6,
                      'Bentley Delivery Centre WA 6983')

    canvas.setFont(BOLD_FONTNAME, LARGE_FONTSIZE)

    current_y -= 36
    current_x += 200

    if draw_page_number:
        canvas.drawString(current_x, current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER), 'PAGE')

    if hasattr(doc, 'licence') and doc.licence.licence_number is not None and doc.licence.licence_sequence:
        canvas.drawString(current_x, current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER) * 2, 'NO.')

    canvas.setFont(DEFAULT_FONTNAME, LARGE_FONTSIZE)

    current_x += 50

    if draw_page_number:
        canvas.drawString(current_x, current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER), str(canvas.getPageNumber()))

    if hasattr(doc, 'licence') and doc.licence.licence_number is not None and doc.licence.licence_sequence:
        canvas.drawString(current_x, current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER) * 2,
                          '%s-%d' % (doc.licence.licence_number, doc.licence.licence_sequence))


def _get_authorised_person_names(application):
    def __find_authorised_persons_dict(data):
        authorised_persons = []
        for item in data:
            if isinstance(item, list):
                authorised_persons = __find_authorised_persons_dict(item)
                if len(authorised_persons) > 0:
                    return authorised_persons
            if isinstance(item, dict):
                if 'authorised_persons' in item:
                    return item['authorised_persons']
                else:
                    for value in item.values():
                        if isinstance(value, list):
                            authorised_persons = __find_authorised_persons_dict(value)
                            if len(authorised_persons) > 0:
                                return authorised_persons

        return authorised_persons

    authorised_person_names = []

    for ap in __find_authorised_persons_dict(application.data):
        if ap.get('ap_given_names') and ap.get('ap_given_names'):
            authorised_person_names.append('%s %s' % (ap['ap_given_names'], ap['ap_surname']))

    return authorised_person_names


def _get_species(application):
    def __find_species_dict(data):
        species = []
        for item in data:
            if isinstance(item, list):
                species = __find_species_dict(item)
                if len(species) > 0:
                    return species
            if isinstance(item, dict):
                if 'species_summary' in item:
                    return item['species_summary']
                else:
                    for value in item.values():
                        if isinstance(value, list):
                            species = __find_species_dict(value)
                            if len(species) > 0:
                                return species

        return species

    species_names_and_count = []

    for s in __find_species_dict(application.data):
        if s.get('species_name') and s.get('species_count'):
            species_names_and_count.append((s['species_name'], s['species_count']))

    return species_names_and_count


def _create_licence(licence_buffer, licence, application, site_url, original_issue_date):
    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN,
                             PAGE_HEIGHT - 160, id='EveryPagesFrame')
    every_page_template = PageTemplate(id='EveryPages', frames=every_page_frame, onPage=_create_licence_header)

    doc = BaseDocTemplate(licence_buffer, pageTemplates=[every_page_template], pagesize=A4)

    # this is the only way to get data into the onPage callback function
    doc.licence = licence
    doc.site_url = site_url

    licence_table_style = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')])

    elements = []

    elements.append(Paragraph(licence.licence_type.act, styles['InfoTitleLargeCenter']))
    elements.append(Paragraph(licence.licence_type.code.upper(), styles['InfoTitleLargeCenter']))
    elements.append(Paragraph(licence.licence_type.name, styles['InfoTitleVeryLargeCenter']))
    elements.append(Paragraph(licence.licence_type.statement, styles['InfoTitleLargeLeft']))
    elements.append(Paragraph(licence.licence_type.authority, styles['InfoTitleLargeRight']))

    # licence conditions
    if application.conditions.exists():
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        elements.append(Paragraph('Conditions', styles['InfoTitleLargeCenter']))
        conditionList = ListFlowable(
            [Paragraph(condition.text, styles['Left']) for condition in application.conditions.all()],
            bulletFontName=BOLD_FONTNAME, bulletFontSize=MEDIUM_FONTSIZE)
        elements.append(conditionList)

    # purpose
    if licence.purpose:
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

        purposes = []
        for purpose in licence.purpose.split('\r\n'):
            if purpose:
                purposes.append(Paragraph(purpose, styles['Left']))
            else:
                purposes.append(Spacer(1, SECTION_BUFFER_HEIGHT))

        elements.append(Table([[Paragraph('Purpose', styles['BoldLeft']), purposes]],
                              colWidths=(100, PAGE_WIDTH - (2 * PAGE_MARGIN) - 100),
                              style=licence_table_style))

    # locations
    if licence.locations:
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

        locations = []
        for location in licence.locations.split('\r\n'):
            if location:
                locations.append(Paragraph(location, styles['Left']))

        elements.append(Table([[Paragraph('Locations', styles['BoldLeft']), locations]],
                              colWidths=(100, PAGE_WIDTH - (2 * PAGE_MARGIN) - 100),
                              style=licence_table_style))

    # authorised persons
    authorised_persons = _get_authorised_person_names(application)
    if len(authorised_persons) > 0:
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        authorised_persons_paragraph = [Paragraph(ap, styles['Left']) for ap in authorised_persons]
        elements.append(Table([[Paragraph('Authorised Persons', styles['BoldLeft']), authorised_persons_paragraph]],
                              colWidths=(100, PAGE_WIDTH - (2 * PAGE_MARGIN) - 100),
                              style=licence_table_style))

    # species
    species = _get_species(application)
    if len(species) > 0:
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        species_names = [Paragraph(s[0], styles['Left']) for s in species]
        species_count = [Paragraph(s[1], styles['Left']) for s in species]
        section_width = (PAGE_WIDTH - (2 * PAGE_MARGIN) - 100) / 2

        elements.append(Table([[Paragraph('Species', styles['BoldLeft']), Paragraph('Name', styles['BoldLeft']),
                                Paragraph('Count', styles['BoldLeft'])],
                               ['', species_names, species_count]],
                              colWidths=(100, section_width, section_width), style=licence_table_style))

    # additional information
    if licence.additional_information:
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

        additional_information_paragraphs = []
        for paragraph in licence.additional_information.split('\r\n'):
            if paragraph:
                additional_information_paragraphs.append(Paragraph(paragraph, styles['Left']))

        elements.append(Table([[Paragraph('Additional Information', styles['BoldLeft']),
                                additional_information_paragraphs]],
                              colWidths=(100, PAGE_WIDTH - (2 * PAGE_MARGIN) - 100),
                              style=licence_table_style))

    # delegation holds the dates, licencee and issuer details.
    delegation = []

    # dates and licensing officer
    dates_licensing_officer_table_style = TableStyle([('VALIGN', (0, 0), (-2, -1), 'TOP'),
                                                      ('VALIGN', (0, 0), (-1, -1), 'BOTTOM')])

    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    date_headings = [Paragraph('Date of Issue', styles['BoldLeft']), Paragraph('Valid From', styles['BoldLeft']),
                     Paragraph('Date of Expiry', styles['BoldLeft'])]
    date_values = [Paragraph(licence.issue_date.strftime(DATE_FORMAT), styles['Left']),
                   Paragraph(licence.start_date.strftime(DATE_FORMAT), styles['Left']),
                   Paragraph(licence.end_date.strftime(DATE_FORMAT), styles['Left'])]

    if original_issue_date is not None:
        date_headings.insert(0, Paragraph('Original Date of Issue', styles['BoldLeft']))
        date_values.insert(0, Paragraph(original_issue_date.strftime(DATE_FORMAT), styles['Left']))

    delegation.append(Table([[date_headings, date_values]],
                            colWidths=(120, PAGE_WIDTH - (2 * PAGE_MARGIN) - 120),
                            style=dates_licensing_officer_table_style))

    # licensee details
    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    address = application.applicant_profile.postal_address
    address_paragraphs = [Paragraph(address.line1, styles['Left']), Paragraph(address.line2, styles['Left']),
                          Paragraph(address.line3, styles['Left']),
                          Paragraph('%s %s %s' % (address.locality, address.state, address.postcode), styles['Left']),
                          Paragraph(address.country.name, styles['Left'])]
    delegation.append(Table([[[Paragraph('Licensee:', styles['BoldLeft']), Paragraph('Address', styles['BoldLeft'])],
                              [Paragraph(render_user_name(application.applicant),
                                         styles['Left'])] + address_paragraphs]],
                            colWidths=(120, PAGE_WIDTH - (2 * PAGE_MARGIN) - 120),
                            style=licence_table_style))

    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Paragraph('Issued by a Wildlife Licensing Officer of the Department of Parks and Wildlife '
                                'under delegation from the Minister for Environment pursuant to section 133(1) '
                                'of the Conservation and Land Management Act 1984.', styles['Left']))

    elements.append(KeepTogether(delegation))

    doc.build(elements)

    return licence_buffer


def _create_letter_header(canvas, doc):
    canvas.setFont(BOLD_FONTNAME, LARGE_FONTSIZE)

    current_y = PAGE_HEIGHT - LETTER_HEADER_MARGIN

    dpaw_header_logo = ImageReader(COLOUR_DPAW_HEADER_LOGO)
    canvas.drawImage(dpaw_header_logo, LETTER_HEADER_MARGIN, current_y - LETTER_IMAGE_HEIGHT,
                     width=LETTER_IMAGE_WIDTH, height=LETTER_IMAGE_HEIGHT)


    canvas.setFillColor(HexColor(0x045690))

    canvas.setFont(DEFAULT_FONTNAME, SMALL_FONTSIZE)

    current_x = 400

    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + LETTER_HEADER_SMALL_BUFFER), 'Your ref:')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + LETTER_HEADER_SMALL_BUFFER) * 2, 'Our ref:')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + LETTER_HEADER_SMALL_BUFFER) * 3, 'Enquiries:')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + LETTER_HEADER_SMALL_BUFFER) * 4, 'Phone:')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + LETTER_HEADER_SMALL_BUFFER) * 5, 'Email:')

    current_x = 450

    canvas.setFillColor(black)

    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + LETTER_HEADER_SMALL_BUFFER), '')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + LETTER_HEADER_SMALL_BUFFER) * 2, '')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + LETTER_HEADER_SMALL_BUFFER) * 3, '')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + LETTER_HEADER_SMALL_BUFFER) * 4, '(08) 9219 9831')

    # draw email address as hyperlink
    email_address = 'wildlifelicensing@dpaw.wa.gov.au'

    current_y = current_y - (SMALL_FONTSIZE + LETTER_HEADER_SMALL_BUFFER) * 5
    canvas.setFillColor(blue)
    canvas.drawString(current_x, current_y, email_address)

    email_address_width = canvas.stringWidth(email_address)

    linkRect = (current_x, current_y, current_x + email_address_width, current_y)
    canvas.linkURL('mailto:{}'.format(email_address), linkRect)


def _create_cover_letter_address(licence):
    addressee = licence.holder
    address = licence.profile.postal_address

    address_elements = []
    address_elements.append(Paragraph(addressee.get_full_name(), styles['Left']))
    address_elements.append(Paragraph(address.line1, styles['Left']))

    if address.line2:
        address_elements.append(Paragraph(address.line2, styles['Left']))

    address_elements.append(Paragraph('{} {} {}'.format(address.locality, address.state, address.postcode),
                                                        styles['Left']))

    return address_elements


def _create_cover_letter(cover_letter_buffer, licence, application, site_url):
    every_page_frame = Frame(LETTER_PAGE_MARGIN, LETTER_PAGE_MARGIN, PAGE_WIDTH - 2 * LETTER_PAGE_MARGIN,
                             LETTER_PAGE_MARGIN - 160, id='EveryPagesFrame')
    every_page_template = PageTemplate(id='EveryPages', frames=every_page_frame, onPage=_create_letter_header)

    doc = BaseDocTemplate(cover_letter_buffer, pageTemplates=[every_page_template], pagesize=A4)

    # this is the only way to get data into the onPage callback function
    doc.site_url = site_url

    elements = []

    elements += _create_cover_letter_address(licence)

    elements.append(Paragraph('Dear {}'.format(licence.holder.get_full_name()), styles['Left']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Paragraph('Please find attached licence', styles['Left']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Paragraph('Please ensure that all the licence conditions are complied with, including the '
                              'forwarding of a return at the end of the licence period.', styles['Left']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    




    # Removed link to online system for beta
    #     elements.append(Paragraph('You also can access it from your Wildlife Licensing dashboard by copying and pasting '
    #                     'the following link in your browser:', styles['Left']))
    #     elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    #     elements.append(Paragraph(site_url, styles['Left']))
    #     elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    #     elements.append(Paragraph("Note: If you haven't been on the Wildlife Licensing site recently you might have to "
    #                               "login first before using the provided link.", styles['Left']))
    #     elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    if licence.cover_letter_message:
        for message in licence.cover_letter_message.split('\r\n'):
            if message:
                elements.append(Paragraph(message, styles['Left']))
            else:
                elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    elements.append(Paragraph('If you have any queries, please contact Mr Danny Stefoni on 9219 9833.'),
                    styles['Left'])
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    elements.append(Paragraph('Yours sincerely,', styles['Left']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT * 3))
    elements.append(Paragraph('from Jim Sharp', styles['Left']))
    elements.append(Paragraph('DIRECTOR GENERAL', styles['Left']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    elements.append(Paragraph(date.today.strftime(DATE_FORMAT), styles['Left']),)

    doc.build(elements)

    return cover_letter_buffer


def _create_licence_renewal_elements(licence):
    return [
        Paragraph('Dear {}'.format(licence.holder.get_full_name()), styles['Left']),
        Paragraph('This is a reminder that your licence:', styles['Left']), Spacer(1, SECTION_BUFFER_HEIGHT),
        Paragraph('{}-{}'.format(licence.licence_number, licence.licence_sequence), styles['BoldLeft']),
        Spacer(1, SECTION_BUFFER_HEIGHT),
        Paragraph('is due to expire on {}.'.format(licence.end_date.strftime(DATE_FORMAT)), styles['Left']),
        Spacer(1, SECTION_BUFFER_HEIGHT),
        Paragraph('Please note that you are required to submit an electronic return and that '
                  'the licence cannot be renewed until this.', styles['Left']),
        Spacer(1, SECTION_BUFFER_HEIGHT),
        Paragraph('If you have any queries, please contact Mr Danny Stefoni on 9219 9833 or '
                  'email to wildlifelicensing@dpaw.wa.gov.au.', styles['Left']),
        Spacer(1, SECTION_BUFFER_HEIGHT), Paragraph('Yours sincerely,', styles['Left']),
        Spacer(1, SECTION_BUFFER_HEIGHT), Paragraph('Jim Sharp', styles['Left']),
        Paragraph('DIRECTOR GENERAL', styles['Left'])
    ]


def _create_licence_renewal(licence_renewal_buffer, licence, site_url):
    every_page_frame = Frame(LETTER_PAGE_MARGIN, LETTER_PAGE_MARGIN, PAGE_WIDTH - 2 * LETTER_PAGE_MARGIN,
                             PAGE_HEIGHT - 160, id='EveryPagesFrame')
    every_page_template = PageTemplate(id='EveryPages', frames=every_page_frame, onPage=_create_letter_header)

    doc = BaseDocTemplate(licence_renewal_buffer, pageTemplates=[every_page_template], pagesize=A4)

    # this is the only way to get data into the onPage callback function
    doc.site_url = site_url

    elements = _create_cover_letter_address(licence) + [Spacer(1, LETTER_ADDRESS_BUFFER_HEIGHT)] + \
        _create_licence_renewal_elements(licence)

    doc.build(elements)

    return licence_renewal_buffer


def _create_bulk_licence_renewal(licences, site_url, buf=None):
    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN,
                             PAGE_HEIGHT - 160, id='EveryPagesFrame')
    every_page_template = PageTemplate(id='EveryPages', frames=every_page_frame, onPage=_create_letter_header)

    if buf is None:
        buf = BytesIO()
    doc = BaseDocTemplate(buf, pageTemplates=[every_page_template], pagesize=A4)

    # this is the only way to get data into the onPage callback function
    doc.site_url = site_url
    all_elements = []
    for licence in licences:
        all_elements += _create_cover_letter_address(licence) + [Spacer(1, LETTER_ADDRESS_BUFFER_HEIGHT)] + \
            _create_licence_renewal_elements(licence)
        all_elements.append(PageBreak())
    doc.build(all_elements)
    return doc


def create_licence_pdf_document(filename, licence, application, site_url, original_issue_date):
    licence_buffer = BytesIO()

    _create_licence(licence_buffer, licence, application, site_url, original_issue_date)

    document = Document.objects.create(name=filename)
    document.file.save(filename, File(licence_buffer), save=True)

    licence_buffer.close()

    return document


def create_licence_pdf_bytes(filename, licence, application, site_url, original_issue_date):
    licence_buffer = BytesIO()

    _create_licence(licence_buffer, licence, application, site_url, original_issue_date)

    # Get the value of the BytesIO buffer
    value = licence_buffer.getvalue()
    licence_buffer.close()

    return value


def create_cover_letter_pdf_document(filename, licence, site_url):
    cover_letter_buffer = BytesIO()

    _create_cover_letter(cover_letter_buffer, licence, site_url)

    document = Document.objects.create(name=filename)
    document.file.save(filename, File(cover_letter_buffer), save=True)

    cover_letter_buffer.close()

    return document


def create_licence_renewal_pdf_bytes(filename, licence, site_url):
    licence_renewal_buffer = BytesIO()

    _create_licence_renewal(licence_renewal_buffer, licence, site_url)

    value = licence_renewal_buffer.getvalue()
    licence_renewal_buffer.close()

    return value


def bulk_licence_renewal_pdf_bytes(licences, site_url):
    doc = None
    try:
        doc = _create_bulk_licence_renewal(licences, site_url)
        return doc.filename.getvalue()
    finally:
        if doc:
            doc.filename.close()


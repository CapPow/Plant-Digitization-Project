from reportlab.platypus import Image, Table, TableStyle, Flowable, SimpleDocTemplate, BaseDocTemplate, PageTemplate, PageBreak
from reportlab.platypus import Frame as platypusFrame   #NOTE SEE Special case import here to avoid namespace conflict with "Frame"
from reportlab.platypus.flowables import Spacer
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.graphics.barcode import code39 #Note, overriding a function from this import in barcode section
from reportlab.lib.units import inch
from reportlab.lib import pagesizes
import os
import sys
import subprocess
from tkinter import filedialog



def genPrintLabelPDFs(labelDataInput):
    labelData = labelDataInput

    xPaperSize = 5.50 * inch   #These values should be user preferences! (But it'll be a PITA to do)
    yPaperSize = 3.50 * inch
    customPageSize = (xPaperSize,yPaperSize)        #set up Paper size for labels, this should be user selectable in time.

    relFont = 12                                    #a font size which everything else relates to. Base normal text font size.

    xMarginProportion = 0
    yMarginProportion = 0   #Padding on tables are functionally the margins in our use. (We're claiming most of paper)
    xMargin = xMarginProportion * xPaperSize        #Margin set up (dynamically depending on paper sizes. Hopefully logical stuff).
    yMargin = xMarginProportion * yPaperSize

    #Style sheets below (lots of stuff.. all style)
    def stylesheet(key):
        styles= {
            'default': ParagraphStyle(
                'default',
                fontName='Times-Roman',
                fontSize=relFont,
                leading=(relFont * 1.1) ,
                leftIndent=0,
                rightIndent=0,
                firstLineIndent=0,
                alignment=TA_LEFT,
                spaceBefore=0,
                spaceAfter=0,
                bulletFontName='Times-Roman',
                bulletFontSize=10,
                bulletIndent=0,
                backColor=None,
                #wordWrap='CJK',
                #wordWrap=(xPaperSize,yPaperSize),
                borderWidth= 0,
                borderPadding= 0,
                borderColor= None,
                borderRadius= None,
                allowWidows= 1,
                allowOrphans= 0,
                textTransform=None,  # 'uppercase' | 'lowercase' | None
                endDots=None,         
                splitLongWords=1,
            ),
        }
        styles['title'] = ParagraphStyle(
            'title',
            parent=styles['default'],
            fontName='Times-Bold',
            fontSize= relFont * 1.2,
            alignment=TA_CENTER,
        )
        styles['collectionNameSTY'] = ParagraphStyle(
            'collectionNameSTY',
            parent=styles['title'],
            fontName='Times',
            fontSize= relFont * 1.2,
            alignment=TA_CENTER,
        )
        styles['samplingEffortSTY'] = ParagraphStyle(
            'samplingEffortSTY',
            parent=styles['title'],
            fontName='Times-Bold',
            fontSize= relFont * 1.18,
            alignment=TA_CENTER,
        )
        styles['dateSTY'] = ParagraphStyle(
            'dateSTY',
            parent=styles['title'],
            fontName='Times',
            fontSize= relFont * 1.18,
            alignment=TA_RIGHT,
        )
        styles['authoritySTY'] = ParagraphStyle(
            'authoritySTY',
            parent=styles['default'],
            fontSize= relFont * 1.18,
            alignment=TA_LEFT
        )
        styles['sciNameSTY'] = ParagraphStyle(
            'sciNameSTY',
            parent=styles['default'],
            fontSize= relFont * 1.18,
            alignment=TA_LEFT,
            spaceAfter = 1
        )
        styles['rightSTY'] = ParagraphStyle(
            'rightSTY',
            parent=styles['default'],
            alignment=TA_RIGHT,
            spaceAfter = 1
        )
        styles['prefixLeftSTY'] = ParagraphStyle(
            'prefixLeftSTY',
            parent=styles['default'],
            alignment=TA_LEFT,
            spaceAfter = 1,
            fontName='Times-Bold'
        )
        styles['prefixRightSTY'] = ParagraphStyle(
            'prefixRightSTY',
            parent=styles['default'],
            alignment=TA_RIGHT,
            spaceAfter = 1,
            fontName='Times-Bold'
        )
        styles['countySTY'] = ParagraphStyle(
            'countySTY',
            parent=styles['default'],
            alignment=TA_CENTER,
            spaceAfter = 1,
            fontName='Times'
        )
        return styles.get(key)

    tableSty = [                                    #Default table style
            ('LEFTPADDING',(0,0),(-1,-1), 0),
            ('RIGHTPADDING',(0,0),(-1,-1), 0),
            ('TOPPADDING',(0,0),(-1,-1), 0),
            ('BOTTOMPADDING',(0,0),(-1,-1), 0)]

    #helper functions to keep the 'flowables' code more legible.

    def Para(textField1,styleKey,prefix = '',suffix = ''):
        if len(dfl(textField1)) > 0 :                #If the field has a value insert it, otherwise blank row
            return Paragraph(('<b>{}</b>'.format(prefix)) + dfl(textField1) + suffix,style = stylesheet(styleKey))
        else:
            return Paragraph('', style = stylesheet(styleKey))

    def sciName(textfield1,textfield2,styleKey,prefix = ''):
        if len(dfl(textfield1)) > 0 :
            return Paragraph(('<i>{}</i>'.format(dfl(textfield1))) + ' ' + dfl(textfield2),style = stylesheet(styleKey))
        else:
            return Paragraph('', style = stylesheet(styleKey))

    def collectedByPara(textfield1,textfield2,styleKey,prefix = ''):
        if len(dfl(textfield1)) > 0 :
            if len(dfl(textfield2)) > 0 :
                return Paragraph(('<b>{}</b>'.format(prefix)) + dfl(textfield1) + ' with ' + dfl(textfield2), style = stylesheet(styleKey))
            else:
                return Paragraph(('<b>{}</b>'.format(prefix)) + dfl(textfield1), style = stylesheet(styleKey))
        else:
            return Paragraph('', style = stylesheet(styleKey))

    def cultivationStatusChecker(textfield1, styleKey):
        if len(dfl(textfield1)) > 0 :
            if int(dfl(textfield1)) > 0 :
                return Paragraph('<b>Cultivated specimen</b>', style = stylesheet(styleKey))
            else:
                return Paragraph('', style = stylesheet('default'))
        else:
            return Paragraph('', style = stylesheet('default'))
        
    def gpsCoordStringer(textfield1,textfield2,textfield3,textfield4,styleKey):
        gpsString = []
        if len(dfl(textfield1)) > 0 :
            if (dfl(textfield1) and dfl(textfield2)):
                # min([len(dfl(textfield1)),len(dfl(textfield2))]) testing length control.
                gpsString.append('<b>GPS: </b>' + dfl(textfield1) + ', ' + dfl(textfield2))
            if dfl(textfield3):
                gpsString.append(' ± ' + dfl(textfield3) + 'm')
            if dfl(textfield4):
                gpsString.append(', <b>Elevation: </b>' + dfl(textfield4) + 'm')

            return Paragraph(''.join(gpsString), style = stylesheet(styleKey))

    #############Logo Work#################################
    ##############################################################################
    #
    #logoPath = 'ucht.jpg'   # This should be determined by the user dialog open option.
    #
    #def getLogo(logoPath):
    #    if logoPath:
    #        return Image(logoPath, width = 40, height =30.6) #These values should be handled dynamically!
    #

    ######Barcode work(Catalog Number)######

    def newHumanText(self):
        return self.stop and self.encoded[1:-2] or self.encoded

    def createBarCodes():   #Unsure of the benefits downsides of using extended vs standard?
        if len(dfl('catalogNumber')) > 0:
            barcodeValue = dfl('catalogNumber')
            code39._Code39Base._humanText = newHumanText  #Note, overriding the human text from this library to omit the stopcode ('+')
            barcode39Std = code39.Standard39(barcodeValue,barHeight=(yPaperSize * .10  ), barWidth=((xPaperSize * 0.10)/72 ), humanReadable=True, quiet = False, checksum=0)
                                             #^^^Note width is automatically (?) in in? adjusting to x/72 seems to make it rational.
            return barcode39Std
        else:
            return ''


    elements = []      #A list to dump the flowables into for pdf generation
    for labelFieldsDict in labelData:
        def dfl(key):                       #dict lookup helper function
            value = labelFieldsDict.get(key,'') #return empty string if no result from lookup.
            return str(value)

    #Building list of flowable elements below
        if len(dfl('catalogNumber')) > 0:                   #If the catalog number is known, add the barcode. If not, don't.
            row0 = Table([[
                Para('collectionName','collectionNameSTY'),
                createBarCodes()
                          ]],
            colWidths = (xPaperSize * .68,xPaperSize * .30), rowHeights = None,

            style = [
                    ('VALIGN',(0,0),(0,-1),'TOP'),
                    ('ALIGN',(0,0),(0,0),'CENTER'),
                    ('ALIGN',(1,0),(1,0),'RIGHT'),
                     ])
        else:
            row0 = Para('collectionName','collectionNameSTY')
                
        
        row1 = Para('samplingEffort','samplingEffortSTY')
     
        row2 = Table([[
            sciName('scientificName','scientificNameAuthorship','sciNameSTY'),
            Para('eventDate','dateSTY')
                      ]],
        colWidths = (xPaperSize * .80,xPaperSize * .18), rowHeights = None,
        style = tableSty)

        row3 = Table([[
                Para('locality','default')]],
                rowHeights=yPaperSize * .15,
                style = tableSty)

        row4 = Table([[
                Para('associatedTaxa','default','Associated taxa: ')]],
                rowHeights=yPaperSize * .15,
                style = tableSty)

        row5 = Table([[
            Para('habitat','default','Habitat: '),
            Para('individualCount','rightSTY', 'Approx. ≥ ',' on site.')]],
            
            colWidths = xPaperSize * .49, rowHeights = None,
            style=tableSty)

        row6 = Table([[
            Para('substrate','default','Substrate: '),
            cultivationStatusChecker('cultivationStatus','rightSTY')]],    
            colWidths = (xPaperSize * .68,xPaperSize * .30), rowHeights = None,
            style=tableSty)

        row7 = [collectedByPara('recordedBy','associatedCollectors','default','Collected by: ')]

        row8 = Table([[
            Para('othercatalognumbers','default','Field Number: '),
            gpsCoordStringer('decimalLatitude', 'decimalLongitude', 'coordinateUncertaintyInMeters', 'minimumElevationInMeters','rightSTY')]],
            
            colWidths = (xPaperSize * .33,xPaperSize * .65), rowHeights = None,
            style=tableSty)


        tableList = [[row0],
                          [row1],
                          [row2],
                          [row3],
                          [row4],
                          [row5],
                          [row6],
                          [row7],
                          [row8],
                        ]
        docTableStyle = [                           #Cell alignment and padding settings (not text align within cells)
                ('VALIGN',(0,3),(0,-1),'BOTTOM'),     #Rows 4-end align to bottom
                ('ALIGN',(0,0),(-1,-1),'CENTER'),     #All rows align to center
                ('LEFTPADDING',(0,0),(-1,-1), 0),     #ALL Rows padding on left to none
                ('RIGHTPADDING',(0,0),(-1,-1), 0),    #ALL Rows padding on right to none
                ('TOPPADDING',(0,0),(-1,-1), 3),      #ALL Rows padding on top to none
                ('BOTTOMPADDING',(0,0),(-1,-1), 0),   #ALL Rows padding on Bottom to none
                ('BOTTOMPADDING',(0,0),(0,0), 3),     #ALL Rows padding on Bottom to none
                ('TOPPADDING',(0,1),(0,1), 6),        #Row 2 top padding to 6
                ('TOPPADDING',(0,2),(0,2), 6),        #Row 3 top padding to 6
                ('BOTTOMPADDING',(0,2),(0,2), 6),     #Row 3 bottom padding to 6
                #('NOSPLIT', (0,0),(-1,-1)),           #Makes Error if it won't fit. We should raise this error to user!
                            ]
        
        docTable = Table(tableList, style = docTableStyle ) #build the table to test it's height

        wid, hei = docTable.wrap(0, 0)      #Determines how much space is used by the table
        spaceRemaining = (yPaperSize - hei - 10) #Determine how much is left on the page
        spaceFiller = [Spacer(width = 0, height = spaceRemaining)]
        tableList.insert(2,spaceFiller)

        docTable = Table(tableList, style = docTableStyle ) #build the final table

        #Add the flowables to the elements list.
        elements.append(docTable)
        elements.append(PageBreak())

    #Build the base document's parameters.
    labelFileName = filedialog.asksaveasfilename(
                                            initialdir=os.getcwd(),
                                            defaultextension='.pdf',
                                            filetypes=(('pdf','*.pdf'),),title = 'Save Labels As')
    doc = BaseDocTemplate(labelFileName,
     pagesize=customPageSize,
     pageTemplates=[],
     showBoundary=0,
     leftMargin=xMargin,
     rightMargin=xMargin,
     topMargin=yMargin,
     bottomMargin=yMargin,
     allowSplitting=1,           
     title=None,
     author=None,
     _pageBreakQuick=1,
     encrypt=None)

    #Function to build the pdf

    def build_pdf(flowables):
        doc.addPageTemplates(
            [
                PageTemplate(
                    frames=[
                        platypusFrame(
                            doc.leftMargin,
                            doc.bottomMargin,
                            doc.width,
                            doc.height,
                            topPadding=0,
                            bottomPadding=0,
                            id=None
                        ),
                    ]
                ),
            ]
        )
        doc.build(flowables)
    #Actually build the pdf
    build_pdf(elements)
    #Open the file after it is built (maybe change/remove this later? Idealy, a preview or something

    def open_file(filename):
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])
    open_file(labelFileName)

# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 19:57:08 2022

NOTE: REQUIRES INSTALLTION OF THE FULL INKSCAPE PROGRAM ON TOP OF CAIROSVG
AND ITS DEPENDANCIES! Please be sure you have them installed before running.
You will need to have permission and then replace all instances of 'My Drive'
with 'Shared drives' to complete Google Drive connectivity. Contact author for
more information.

@author: ian.michael.bollinger@gmail.com | ian@hyphaelabs.org
"""

###############################################################################
# Load Necessary Libraries to import images and organize PDF Reports
###############################################################################
import os
from fpdf import FPDF
import cairosvg
import pandas as pd
###############################################################################
    
###############################################################################
# Function to add PNG to a PDF
###############################################################################
def add_png_to_pdf(image_name, x_pos, y_pos, image_w, image_h):
    if os.path.exists(image_name):   
        pdf.image(image_name, x_pos, y_pos, image_w, image_h)
        
    else:
        print("File not found:", image_name)
    print(f"{image_name} Added")
###############################################################################

###############################################################################
# Function to add SVG to a PDF by converting with CairoSVG
###############################################################################
def cairo_add_svg_to_pdf(sample_id,graphic_type,input_w,input_h,pdf_x,pdf_y):
    input_path = f'{sample_id}-{graphic_type}.svg'
    input_png = f'{sample_id}-{graphic_type}.png'
    cairosvg.svg2png(url=input_path, write_to=input_png)
    add_png_to_pdf(input_png, pdf_x, pdf_y, input_w, input_h)
###############################################################################

###############################################################################
# Function to add SVG to a PDF by converting with Inkscape
# Use Inkscape to convert SVG to PNG because CairoSVG distorts the text
###############################################################################
def inkscape_add_svg_to_pdf(sample_id,graphic_type,input_w,input_h,pdf_x,pdf_y):
    input_path = f'{sample_id}-{graphic_type}.svg'
    input_png = f'{sample_id}-{graphic_type}.png'    
    os.system(f'inkscape --export-type=png {input_path}')
    add_png_to_pdf(input_png, pdf_x, pdf_y, input_w, input_h)
###############################################################################

###############################################################################
# Function to Generate the PDF Workspace's first page and populate it
###############################################################################
def generate_report():
    global pdf
    pdf = FPDF()
    pdf.add_page()
    
    # Add Template Graphics
    HL_logo_path = template_dir + "HLchemprofbanner.png"
    HL_logo_w, HL_logo_h = 100, 20
    HL_logo_x, HL_logo_y = 10, 10
    add_png_to_pdf(HL_logo_path, HL_logo_x, HL_logo_y, HL_logo_w, HL_logo_h)

    # Add Template Graphics
    tryp_logo_path = template_dir + "tryptomicssupport.png"
    tryp_logo_w, tryp_logo_h = 32, 10
    tryp_logo_x, tryp_logo_y = 110, 18
    add_png_to_pdf(tryp_logo_path, tryp_logo_x, tryp_logo_y, tryp_logo_w, tryp_logo_h)
    
    # Check For Report Type and add appropriate graphics
    if report_type == 'Default':
        compile_default_report()
    elif report_type == 'Church':
        compile_church_report()
    else:
        print(f'ERROR IN GENERATING REPORT: {report_type}')
    
    # Save the Generated PDF of the sample
    pdf.output(f"{sample_dir}/{sample_id} - {sample_name}.pdf", "F")
    print()
###############################################################################

###############################################################################
# Function to Compile Graphics and Tables for Chemical Profile & Dose Report
###############################################################################
def compile_default_report():
    default_report_list = [['sample_table', 10, 30, 186, 50],
                           ['description_table_top', 10, 79.5, 186, 12],
                           ['description_table_bot', 10, 91.5, 186, 61],
                           [f'{images_dir}{sample_id}-W.png', 11, 92, 56, 56],
                           [f'{images_dir}{sample_id}-H.png', 104, 92, 56, 56],
                           ['donut_plot', 10, 149, 93, 105],
                           ['legend_table', 108, 149, 88, 105], # IS PIXELATED
                           ['dose_table', 10, 255, 186, 32]]
    
    default_report_df = pd.DataFrame(default_report_list,
                                     columns = ['graphic_type',
                                                'pdf_x','pdf_y',
                                                'input_w','input_h'])
    
    for index, row in default_report_df.iterrows():
        if row['graphic_type'] == 'description_table_bot':
            inkscape_add_svg_to_pdf(sample_id,row['graphic_type'],
                                    row['input_w'], row['input_h'],
                                    row['pdf_x'], row['pdf_y'])
        elif '-W' in row['graphic_type'] or '-H' in row['graphic_type']:
            add_png_to_pdf(row['graphic_type'],
                           row['pdf_x'], row['pdf_y'],
                           row['input_w'], row['input_h'])
        else:
            cairo_add_svg_to_pdf(sample_id,row['graphic_type'],
                                 row['input_w'], row['input_h'],
                                 row['pdf_x'], row['pdf_y'])     
###############################################################################

###############################################################################
# Function to Compile Graphics and Tables for Church of Ambrosia Report
###############################################################################
def compile_church_report():
    """
    COMING SOON
    """
    print('COMING SOON - NO CHURCH REPORT GENERATED')
###############################################################################

###############################################################################
#
# MAIN: Iterate over Sample Directories & Set Tempalte/Square Image Directories
#
###############################################################################
global sample_id
global sample_name
global sample_dir
global report_type
workspace_dir = 'H:/My Drive/HL Data Files/AUTOMATION WORKSPACE/'
template_dir = 'H:/My Drive/HL Data Files/AUTOMATION WORKSPACE/Template/'
images_dir = 'H:/My Drive/HL Data Files/Sample Images/SQUARE/'
subfolders = [ f.path for f in os.scandir(workspace_dir) if f.is_dir() ]
for sample_dir in subfolders:
    if sample_dir == 'H:/My Drive/HL Data Files/AUTOMATION WORKSPACE/Template':
        pass
    else:
        os.chdir(sample_dir) 
        sample_info = sample_dir.split(workspace_dir)[1]
        report_type = sample_info.split(' - ')[0]
        sample_id = sample_info.split(' - ')[1]
        sample_name = sample_info.split(' - ')[2]
        generate_report()
###############################################################################
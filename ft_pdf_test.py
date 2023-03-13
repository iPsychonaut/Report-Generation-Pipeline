# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 11:30:57 2023

@author: theda
"""
###############################################################################
# Load Necessary Libraries to import images and organize PDF Reports
###############################################################################
import os
from fpdf import FPDF
import cairosvg
import pandas as pd
import configparser
from PIL import Image

global sample_id
global sample_name
global sample_dir
global section_title_dict
global profile_images_dir

###############################################################################
# Function to add PNG to a PDF
###############################################################################
def add_png_to_pdf(image_name, x_pos, y_pos, image_w, image_h):
    jpg_name = image_name.replace('png','jpg')
    if not os.path.exists(image_name): 
        print(f"File not found: {image_name}\nUsing Default Image")
        pdf.image(f'{template_dir}/default_image.png', x_pos, y_pos, image_w, image_h) 
    elif '-M' in image_name:
        img = Image.open(image_name).convert('RGBA')
        new_img = Image.new('RGBA', img.size (255,255, 255, 0))
        # Blend the original image with the new transparent image using alpha=0.2 (20% transparency)
        transp_img = Image.blend(new_img, img, alpha=0.2)
        transp_img.save(f'{sample_id}-transp-M.png')
        pdf.image(f'{sample_id}-transp-M.png', x_pos, y_pos, image_w, image_h) 
    elif os.path.exists(image_name):   
        pdf.image(image_name, x_pos, y_pos, image_w, image_h)
    elif os.path.exists(jpg_name):   
        pdf.image(jpg_name, x_pos, y_pos, image_w, image_h) 

    print(f"{image_name} Added")
###############################################################################

###############################################################################
# Function to add SVG to a PDF by converting with CairoSVG
###############################################################################
def cairo_add_svg_to_pdf(sample_id,graphic_type,input_w,input_h,pdf_x,pdf_y):
    print(sample_id,graphic_type,input_w,input_h,pdf_x,pdf_y)
    input_path = f'{sample_id}-{graphic_type}.svg'
    input_png = f'{sample_id}-{graphic_type}.png'
    if 'Template' in graphic_type:
        input_path = graphic_type
        input_png = graphic_type.replace('svg','png')
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


def build_report(input_list):
    input_df = pd.DataFrame(input_list,
                                      columns = ['graphic_type',
                                                'pdf_x','pdf_y',
                                                'input_w','input_h'])    
    for index, row in input_df.iterrows():
        if row['graphic_type'] == 'description_table_bot':
            inkscape_add_svg_to_pdf(sample_id,row['graphic_type'],
                                    row['input_w'], row['input_h'],
                                    row['pdf_x'], row['pdf_y'])
        elif '-W' in row['graphic_type'] or '-H' in row['graphic_type'] or '-M' in row['graphic_type']:
            add_png_to_pdf(row['graphic_type'],
                            row['pdf_x'], row['pdf_y'],
                            row['input_w'], row['input_h'])
        else:
            cairo_add_svg_to_pdf(sample_id,row['graphic_type'],
                                  row['input_w'], row['input_h'],
                                  row['pdf_x'], row['pdf_y'])

def generate_report(report_type, save_dir, section_title, s):
    global pdf
    pdf = FPDF()
    pdf.add_page()
 
    # Add HL Logo
    HL_logo_path =  f"{template_dir}/HL_transparent.png"
    pdf.image(HL_logo_path, 10, 9, 80, 20)
    
    # Add Sample ID Banner
    cairo_add_svg_to_pdf(sample_id,'sample_table_name_id',191,10.269,10,30)
    
    
    # define the styles for the text
    pdf.set_font('Arial','', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)

    # Add Section ttile
    pdf.set_xy(88, 10)
    pdf.multi_cell(0, 6, section_title)
    
    if report_type == 'Cup':
        print('DO CUP PROFILE REPORT')
        # GENERATE CHAMP DICTS ########################## UPDATE FOR EVERY CUP
        champ_dict = {'Micro' : 'CUP265',
                      'Rec/Out': 'CUP282',
                      'Therapy' : 'CUP314',
                      'Spiritual' : 'CUP319',
                      'Profile' : 'CUP311'}
        champ_logo_dict = {'Micro' : 'HCFall22-Micro.png',
                           'Rec/Out': 'HCFall22-Rec.png',
                           'Therapy' : 'HCFall22-Therapy.png',
                           'Spiritual' : 'HCFall22-Spirit.png',
                           'Profile' : 'HCFall22-Unique.png'}
        
        # Add Support Logos ########################## UPDATE FOR EVERY CUP
        tryp_logo_path =  f"{template_dir}/tryptomicssupport.png"
        tryp_logo_w, tryp_logo_h = 32, 10
        tryp_logo_x, tryp_logo_y = 164, 17.5
        add_png_to_pdf(tryp_logo_path, tryp_logo_x, tryp_logo_y, tryp_logo_w, tryp_logo_h)
        
        for key, value in champ_dict.items():
            print(value)
            print(sample_id)
            if value == sample_id:
                    print(f"{sample_id} ADD CUSTOM LOGO {key} CHAMP")
                    champ_logo = champ_logo_dict.get(key)
                    champ_ribbon = champ_logo.split('-')[1]
                    cup_logo_path = f"{template_dir}/{champ_logo}"
                    cup_logo_w, cup_logo_h = 52, 15
                    cup_logo_x, cup_logo_y = 109.5, 12
                    add_png_to_pdf(cup_logo_path, cup_logo_x, cup_logo_y, cup_logo_w, cup_logo_h)
                    champ_ribbon_path = f"{template_dir}/{champ_ribbon}"
                    champ_ribbon_w, champ_ribbon_h = 51, 50
                    champ_ribbon_x, champ_ribbon_y = 110, 40
                    add_png_to_pdf(champ_ribbon_path, champ_ribbon_x, champ_ribbon_y, champ_ribbon_w, champ_ribbon_h)
                    break
            else:
                print(f"{sample_id} ADD DEFAULT LOGO CUP.")
                cup_logo_path = f"{template_dir}/HCFall22-banner.png"
                cup_logo_w, cup_logo_h = 52, 15
                cup_logo_x, cup_logo_y = 109.5, 12
                add_png_to_pdf(cup_logo_path, cup_logo_x, cup_logo_y, cup_logo_w, cup_logo_h)
        
        indiv_report_list = [['sample_table_client', 10, 40, 186, 10],
                                   ['sample_table_cultivar', 10, 50, 186, 10],
                                   ['sample_table_gen_date', 10, 60, 186, 10],
                                   ['sample_table_species', 10, 70, 186, 10],
                                   ['description_table_top', 10, 80, 186, 10],
                                   ['description_table_bot', 10, 90, 186, 61],
                                   [f'{profile_images_dir}/{sample_id}-W.png', 11, 91, 56, 56],
                                   [f'{profile_images_dir}/{sample_id}-H.png', 104, 91, 56, 56],
                                   ['donut_plot', 5, 148.5, 105, 105],
                                   ['legend_table', 108, 149, 88, 105],
                                   ['dose_table', 10, 253, 186, 37]]
        build_report(indiv_report_list)
        
        
    # GENERATE INDIVIDUAL CHEMICAL PROFILE REPORT
    elif report_type == 'Profile':
        print('DO CHEM PROFILE REPORT')
        indiv_report_list = [['sample_table_client', 10, 40, 186, 10],
                                   ['sample_table_cultivar', 10, 50, 186, 10],
                                   ['sample_table_gen_date', 10, 60, 186, 10],
                                   ['sample_table_species', 10, 70, 186, 10],
                                   ['description_table_top', 10, 80, 186, 10],
                                   ['description_table_bot', 10, 90, 186, 61],
                                   [f'{profile_images_dir}/{sample_id}-W.png', 11, 91, 56, 56],
                                   [f'{profile_images_dir}/{sample_id}-H.png', 104, 91, 56, 56],
                                   ['donut_plot', 5, 148.5, 105, 105],
                                   ['legend_table', 108, 149, 88, 105],
                                   ['dose_table', 10, 253, 186, 37]]
        build_report(indiv_report_list)
    
    # GENERATE FLUSH TEST REPORTS
    elif report_type == 'Flush':
        print('DO FLUSH TEST REPORT')
        if s == 0:
            indiv_report_list = [['sample_table_client', 10, 40, 186, 10],
                                       ['sample_table_cultivar', 10, 50, 186, 10],
                                       ['sample_table_gen_date', 10, 60, 186, 10],
                                       ['sample_table_species', 10, 70, 186, 10],
                                       ['description_table_top', 10, 80, 186, 10],
                                       ['description_table_bot', 10, 90, 186, 61],
                                       [f'{profile_images_dir}/{sample_id}-W.png', 11, 91, 56, 56],
                                       [f'{profile_images_dir}/{sample_id}-H.png', 104, 91, 56, 56],
                                       ['donut_plot', 5, 148.5, 105, 105],
                                       ['legend_table', 108, 149, 88, 105],
                                       ['dose_table', 10, 253, 186, 37]]
            build_report(indiv_report_list)
        elif s == 1:
            flush_heat_report_list = [['indiv_flush_bar',8,40.5,191,136.429],
                                      [f'{template_dir}/rec_use_spec.svg', 185, 56.5, 21.5, 107.5],
                                      ['indiv_flush_table',10,180,106.7,68.5],
                                      ['pcb-pcn-heatmap_plot', 120, 180, 70, 70],
                                      [f'{flush_images_dir}/{sample_id}-M.png', 121.5, 189.5, 56.5, 59]]
            build_report(flush_heat_report_list)
        elif s == 2:
            flush_feature_report_list = [['sample_table_name_id', 10, 30, 186, 10],
                                         ]
            build_report(flush_feature_report_list)
    
    # Save the Generated PDF of the sample
    report_name = f'{save_dir}/{sample_id} - {sample_name} - {s+1}.pdf'
    print(report_name)
    pdf.output(report_name, "F")
    print()



# Use Python's built-in configparser library to parse the variables in the config.txt file
config = configparser.ConfigParser()
config.read('C:/Users/theda/OneDrive/Documents/Python\HL/config.txt')

automation_workspace = config.get('DEFAULT', 'automation_workspace')
template_dir = config.get('DEFAULT', 'template_dir')

profile_images_dir = config.get('DEFAULT', 'profile_images_dir')
flush_images_dir = config.get('DEFAULT', 'flush_images_dir')

subfolders = [ f.path for f in os.scandir(automation_workspace) if f.is_dir() ]
HL_logo_path = f'{template_dir}/HL_transparent.png'
report_name = ''

os.chdir(automation_workspace)

section_title_dict = {'Flush':   ['FLUSH TEST AVERAGE\nCHEMICAL PROFILE &\nDOSE REPORT',
                                  'FLUSH TEST PROFILES\nPCB+PCN DISTRIBUTION &\nHEAT MAP' ,
                                  'FLUSH TEST\nMACHINE LEARNING STATISTICAL ANLAYSIS\nOF PCB+PCN POTENCY VARIANCE'],
                      'Profile': ['CHEMICAL\nPROFILE &\nDOSE REPORT'],
                      'Cup':     ['HYPHAE CUP\nCHEMICAL PROFILE &\nDOSE REPORT']}

for sample_dir in subfolders:
    if 'Template' in sample_dir:
        pass
    else:
        os.chdir(sample_dir)    
        sample_info = sample_dir.split(automation_workspace)[1]
        report_type = sample_info.split(' - ')[0]
        sample_id = sample_info.split(' - ')[1]
        sample_name = sample_info.split(' - ')[2]
        if 'CUP' in report_type or 'Cup' in report_type: 
            report_type = 'Cup'
            for s, section_title in enumerate(section_title_dict[report_type]):
                pass
                # if not os.path.exists(report_name):
                #     generate_report(report_type, sample_dir, section_title, s)
        elif 'Profile' in report_type:
            report_type = 'Profile'
            for s, section_title in enumerate(section_title_dict[report_type]):
                pass
                # if not os.path.exists(report_name):
                #     generate_report(report_type, sample_dir, section_title, s)
        elif 'Flush'  in report_type or 'FLUSH' in report_type or 'FT'  in report_type:
            report_type = 'Flush'
            for s, section_title in enumerate(section_title_dict[report_type]):
               if not os.path.exists(report_name):
                   generate_report(report_type,sample_dir, section_title, s)
            ft_subfolders = [ f.path for f in os.scandir(sample_dir) if f.is_dir() ]
            for flush_dir in ft_subfolders:
                if flush_dir == f'{sample_dir}\catboost_info':
                    pass
                else:
                    os.chdir(flush_dir)   
                    sample_info = flush_dir.split(f'{sample_dir}\\')[1]
                    report_type = 'Flush'
                    sample_id = sample_info
                    print(flush_dir)
                    generate_report(report_type, flush_dir, section_title_dict[report_type][0], 0)
                    generate_report(report_type, flush_dir, section_title_dict[report_type][1], 1)



# -*- coding: utf-8 -*-

import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import plot

pio.renderers.default='svg'

def item_id_table_generator(sample_id, sample_name):
    # Generate Sample Name & ID Table
    header_values = ['ITEM ID & NAME:', f"{sample_id} - {sample_name}"]
    header_align = ['right', 'left']
    header_fill = dict(color='black')
    header_line = dict(width=1, color='black')
    header_font = dict(family="Arial", size=[35,45], color='white')
    header_height = 75
    sample_table_name_id = go.Figure(data=[go.Table(header=dict(values=header_values, align=header_align, fill=header_fill, line=header_line, font=header_font, height=header_height),
                                                      columnwidth=[451, 1000])],
                                      layout=go.Layout(height=75, width=1325, autosize=False,
                                                        margin=dict(l=0, r=0, b=0, t=0, pad=4),
                                                        showlegend=False))
    # Display the table and save it as an SVG image
    #plot(sample_table_name_id)
    sample_table_name_id_output_filename = f"{sample_id}-sample_table_name_id.svg"
    sample_table_name_id.write_image(sample_table_name_id_output_filename)

def profile_table_generator(sample_id, sample_name, sample_info_df): 
    sample_client = sample_info_df['Client_Name']
    sample_species = sample_info_df['Species_of_Origin']
    
    if sample_info_df['Cultivar'] == '':
        sample_cultivar = sample_info_df['Sample_Name']
    else:
        sample_cultivar = sample_info_df['Cultivar']
    cultivar_font_size = 30
    if len(sample_cultivar) > 62:
        delta_len = len(sample_cultivar)-62
        cultivar_font_size = (cultivar_font_size-(2.5*(round(delta_len/6,0))))
        
    sample_gen_date = sample_info_df['Generation_Date']
    sample_client_desc =  sample_info_df['Client_Notes']
    if sample_info_df['Lab_Description'] == '':
        sample_lab_desc = 'Information not availble.'
    else:
        sample_lab_desc = sample_info_df['Lab_Description']
    if sample_info_df['Homogenized_Description'] == '':
        sample_homog_desc = 'Information not availble.'
    else:
        sample_homog_desc = sample_info_df['Homogenized_Description']
        
    sample_info_table_generator(sample_id, sample_client, sample_species, sample_cultivar, cultivar_font_size, sample_gen_date, sample_client_desc)
    lab_table_generator(sample_id, sample_lab_desc, sample_homog_desc)

def sample_info_table_generator(sample_id, sample_client, sample_species, sample_cultivar, cultivar_font_size, sample_gen_date, sample_client_desc):
    # Generate Sample Client Table
    sample_table_client = go.Figure(data=[go.Table(
                                columnwidth=[451,1000],
                                header=dict(
                                    values=['<b>CULTIVATOR/PRODUCER:<b>',f'<br><br>{sample_client}'],
                                    align=['right','left'],
                                    fill=dict(color=['lightgrey', 'white']),
                                    line=dict(width=1, color='black'),
                                    font=dict(family='Arial', size=[30,30], color='black'),
                                    height=70))])
    sample_table_client.update_layout(
        height=70,
        width=1325,
        autosize=False,
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        showlegend=False)
    # Display the table and save it as an SVG image
    #plot(sample_table_client)
    sample_table_client_output_filename = f"{sample_id}-sample_table_client.svg"
    sample_table_client.write_image(sample_table_client_output_filename)
    
    # Generate Sample Species Table
    sample_table_species = go.Figure(data=[go.Table(
        columnorder=[1, 2],
        columnwidth=[451, 1000],
        header=dict(
            values=["<b>SPECIES:<b>", f'<br><br><i>{sample_species}<i>'],
            align=["right", "left"],
            fill_color=["lightgrey", "white"],
            line=dict(width=1, color="black"),
            font=dict(family="Arial", size=[30, 30], color="black"),
            height=70,))])
    sample_table_species.update_layout(
        height=70,
        width=1325,
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        showlegend=False,
        autosize=False,)
    # Display the table and save it as an SVG image
    #plot(sample_table_species)
    sample_table_species_output_filename = f"{sample_id}-sample_table_species.svg"
    sample_table_species.write_image(sample_table_species_output_filename)
    
    # Generate Sample Cultivar Table
    sample_table_cultivar = go.Figure(data=[go.Table(
        header=dict(values=["<b>CULTIVAR:<b>", f'<br>{sample_cultivar}'],
                    align=['right', 'left'],
                    fill=dict(color=['lightgrey', 'white']),
                    line=dict(width=1, color='black'),
                    font=dict(family="Arial", size=[30, cultivar_font_size], color='black'),
                    height=70),
        columnwidth=[451, 1000])])
    sample_table_cultivar.update_layout(
        height=70,
        width=1325,
        autosize=False,
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        showlegend=False)
    # Display the table and save it as an SVG image
    #plot(sample_table_cultivar)
    sample_table_cultivar_output_filename = f"{sample_id}-sample_table_cultivar.svg"
    sample_table_cultivar.write_image(sample_table_cultivar_output_filename)
    
    # Generate Sample Generation Date Table
    sample_table_gen_date = go.Figure(data=[go.Table(
        header=dict(values=["<b>GENERATION DATE:<b>", f'<br>{sample_gen_date}'],
                    align=['right', 'left'],
                    fill=dict(color=['lightgrey', 'white']),
                    line=dict(width=1, color='black'),
                    font=dict(family="Arial", size=[30, 30], color='black'),
                    height=70),
        columnwidth=[451, 1000])])
    sample_table_gen_date.update_layout(
        height=70,
        width=1325,
        autosize=False,
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        showlegend=False)
    # Display the table and save it as an SVG image
    #plot(sample_table_gen_date)
    sample_table_gen_date_output_filename = f"{sample_id}-sample_table_gen_date.svg"
    sample_table_gen_date.write_image(sample_table_gen_date_output_filename)
    
    sample_client_desc_font = 30
    if len(sample_client_desc) > 95:
        sample_client_desc_font = 20
        sample_client_desc = f'{sample_client_desc.split(". ")[0]}.<br>{sample_client_desc.split(". ")[1]}'
    elif len(sample_client_desc) > 65:
        sample_client_desc_font = 25
    # Generate Sample Client Notes Table
    description_table_top = go.Figure(data=[go.Table(
        header=dict(values=["<b>SUBMITTOR NOTES:<b>", f'<br>{sample_client_desc}'],
                    align=['right', 'left'],
                    fill=dict(color=['lightgrey', 'white']),
                    line=dict(width=1, color='black'),
                    font=dict(family="Arial", size=[30, sample_client_desc_font], color='black'),
                    height=70),
        columnwidth=[451, 1000])])
    description_table_top.update_layout(
        height=70,
        width=1325,
        autosize=False,
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        showlegend=False)
    # Display the table and save it as an SVG image
    #plot(description_table_top)
    description_table_top_output_filename = f"{sample_id}-description_table_top.svg"
    description_table_top.write_image(description_table_top_output_filename)


def lab_table_generator(sample_id, sample_lab_desc, sample_homog_desc):
    # Generate Bottom Half of Description Table
    description_table_bot_name = f"{sample_id}-description_table_bot.svg"
    description_table_bot = go.Figure(data=[go.Table(    columnwidth=[451,273,451,273],
        header=dict(
            values=['', sample_lab_desc, '',sample_homog_desc],
            align=['left'],
            fill=dict(color='white'),
            line=dict(width=1, color='black'),
            font=dict(family="Arial", size=25, color='black'),
            height=405))])
    description_table_bot.update_layout(
        height=425,
        width=1325,
        autosize=False,
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        showlegend=False)
    # Display the table and save it as an SVG image
    #plot(description_table_bot)
    description_table_bot_output_filename = f"{sample_id}-description_table_bot.svg"
    description_table_bot.write_image(description_table_bot_output_filename)

# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 11:46:33 2022

@author: theda
"""
###############################################################################
# IMPORT LIST
###############################################################################

import pandas as pd
import numpy as np
import pygsheets
from datetime import datetime
import os
import plotly 
import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import plot
from plotly.subplots import make_subplots
import colorlover as cl
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from catboost import CatBoostRegressor
import configparser

def convert_ppm_mg_g(sample_id, sample_wt, extraction_vol, extract_dil, compound_ppm):
    """
    Returns the mg/g value of a compound based on its ppm value and the experimental parameters
    of the sample weight, extraction volume, and extract dilution factor.
    
    Parameters:
    - sample_wt: float
        The weight of the sample in grams.
    - extraction_vol: float
        The volume of the extraction solvent used in milliliters.
    - extract_dil: float
        The dilution factor of the extract.
    - compound_ppm: float
        The ppm value of the compound.
    - sample_id: str
        The search term to use when selecting rows.
    
    Returns:
    - compound_mg_g: float
        The mg/g value of the compound.
    """
    if compound_ppm == 0 or compound_ppm == '':
        compound_mg_g = 0
    else:
        try:
            compound_ppm = float(compound_ppm)
        except ValueError:
            print(f'Could not convert {sample_id} ppm string to float: {compound_ppm}')
        try:
            compound_mg_g = (extraction_vol/sample_wt)*(compound_ppm)*(1/1000)    
        except TypeError:
            print(f'{sample_id} has a type error in the following:\n sample_wt: {sample_wt}\n extraction_vol: {extraction_vol}\n extract_dil: {extract_dil}\n compound_ppm: {compound_ppm}')
            compound_mg_g = 0
    compound_mg_g = round(compound_mg_g, 1)
    return(compound_mg_g)

def load_worksheet_from_gsheet(service_file_path, gsheet_key, sheet_name):
    """
    Returns a pandas DataFrame that contains data from a specified sheet in a Google Spreadsheet.

    Parameters:
    - service_file_path: str
        The file path of the JSON file containing Google API credentials.
    - gsheet_key: str
        The unique key of the Google Spreadsheet.
    - sheet_name: str
        The name of the sheet to load data from.
    
    Returns:
    - loaded_df: pandas DataFrame
        The DataFrame containing the data from the specified sheet.
    """
    # Authorize Google Sheets API with credentials file
    google_credentials = pygsheets.authorize(service_file=service_file_path)
    
    # Open the Google Spreadsheet
    loaded_spreadsheet = google_credentials.open_by_key(gsheet_key)
    
    # Select the sheet and load the data as a DataFrame
    current_worksheet = loaded_spreadsheet.worksheet_by_title(sheet_name)
    loaded_df = current_worksheet.get_as_df()
    
    return loaded_df, loaded_spreadsheet

def save_archive_worksheet(loaded_df, loaded_spreadsheet):
    """
    Saves the given DataFrame as a new worksheet in the given Google Spreadsheet,
    using the current date and time to generate a unique name for the worksheet.

    Parameters:
    - loaded_df: pandas DataFrame
        The DataFrame to save as a new worksheet.
    - loaded_spreadsheet: pygsheets.Spreadsheet
        The pygsheets.Spreadsheet object representing the Google Spreadsheet to save to.

    Returns:
    - None
    """
    # Get the current date and time and format it to '20220101-2359'
    now = datetime.now()
    date_time_str = now.strftime("%Y%m%d-%H%M")

    # Generate New Archive worksheet in the loaded Google Spreadsheet
    update_sheet_name = f'ArchiveDataFrame-{date_time_str}'
    try:
        loaded_spreadsheet.add_worksheet(update_sheet_name)
    except:
        pass
    new_worksheet = loaded_spreadsheet.worksheet_by_title(update_sheet_name)
    new_worksheet.clear('A1',None,'*')
    new_worksheet.set_dataframe(loaded_df, (1,1), encoding='utf-16', fit=True)
    new_worksheet.frozen_rows = 1
    new_worksheet.frozen_cols = 2

def calculate_mg_g_values(loaded_df, sample_id):
    """
    Returns a new DataFrame containing only the rows where the 'Sample_ID'
    column contains the given search term. It then calculates the 'mg_g'
    values for the selected rows using the 'ppm' values and returns the
    updated DataFrame.

    Parameters:
    - loaded_df: pandas DataFrame
        The DataFrame to search and update.
    - sample_list: list
        The search term to use when selecting rows.

    Returns:
    - updated_df: pandas DataFrame
        The updated DataFrame with 'mg_g' values calculated for the selected rows.
    """
    
    # get a list of column names that contain 'ppm'
    ppm_col_list = [col for col in loaded_df.columns if 'ppm' in col]

    # get a list of column names that contain 'mg_g'
    mg_g_col_list = [col for col in loaded_df.columns if 'mg_g' in col]

    mg_g_mean_col_list = [col.replace('mg_g','mg_g_MEAN') for col in loaded_df.columns if 'mg_g' in col]
    mg_g_SD_col_list = [col.replace('mg_g','mg_g_SD') for col in loaded_df.columns if 'mg_g' in col]

    # create a new dataframe containing only the rows where 'Sample_ID' contains the search term
    specific_sample_df = loaded_df[loaded_df['Sample_ID'].str.contains(sample_id)].copy()

    for r, replicate in specific_sample_df.iterrows():
        extraction_vol = replicate['Sonication_Solvent_Volume']
        extract_dil = replicate['Extract_Dilution_Factor']
        sample_wt = replicate['Processed_Amount']
        for i, ppm_col in enumerate(ppm_col_list):
            compound_ppm = replicate[ppm_col]
            compound_mg_g = convert_ppm_mg_g(sample_id, sample_wt, extraction_vol, extract_dil, compound_ppm)
            specific_sample_df.loc[r, mg_g_col_list[i]] = compound_mg_g

    # update the original DataFrame with the updated rows
    updated_df = loaded_df.copy()
    updated_df.update(specific_sample_df)

    return updated_df

def stats_df_generator(df):
    """
    Returns a tuple containing statistics for a specific sample in a loaded DataFrame.
    
    Parameters:
    - sample_id: str
        The search term to use when selecting rows.
    - loaded_df: pd.DataFrame
        The DataFrame containing the data.
    
    Returns:
    - A tuple containing the sample ID, sample name, a list of compound names, a list of mean values,
      and a list of standard deviation values.
    """
    
    # Extract sample name from first row
    sample_name = df.iloc[0, 1]
    sample_info_df = df.iloc[0, :df.columns.get_loc('Sonication_Solvent_Volume')]

    
    # Initialize empty lists for compound names, means, and standard deviations
    full_compound_list = []
    full_mean_data = []
    full_sd_data = []
    
    # Iterate over columns and calculate mean and standard deviation for columns containing 'mg_g'
    for i, col in enumerate(df.columns):
        if 'mg_g' in col:
            full_compound_list.append(col.replace('_mg_g', ''))
            mean_value = round(df[col].mean(), 1)
            sd_value = round(df[col].std(), 1)
            full_mean_data.append(mean_value)
            full_sd_data.append(sd_value)
        
    # Return the collected data as a tuple
    return (sample_info_df, full_compound_list, full_mean_data, full_sd_data)

###############################################################################
#
# Standard Sample Graphics Generator
#
###############################################################################

def profile_graphics_generator(sample_id, sample_name, full_compound_list, full_mean_data, full_sd_data):    
    """
    Generates the Donut Graphic, Legend Table, and Reccomended Dose Chart based on the mean data for sample_id.
    
    Parameters:
    - sample_id: str
        The search term to use when selecting rows.
    - sample_name: str
        The name of the sample.
    - full_compound_list: list
        Full list of all compounds to be represented.           
    - full_mean_data: list
        List containing the mean mg/g data for all compounds.
    - full_sd_data: list
        List containing the standard deviation mg/g data for all compounds.
    
    Returns:
    - Nothing
    """    
    # Build out for Donut Graphic Data
    abrv_dict = {
        'known': {'DMT': 'NN-DMT', 'PCB': 'Psilocybin', 'PCN': 'Psilocin', 'BUF': 'Bufotenin', '5MEO': 'Five-MEO-DMT'},
        'other': {'ADN': 'Adenosine', 'CDY': 'Cordycepin', 'TRP': 'Tryptamine', 'BAO': 'Baeocystin', 
                  'NPC': 'Norpsilocin', 'NRB': 'Norbaeocystin', 'ARG': 'Aeruginascin', '4HTMT': 'Four-HTMT'}}
    
    # Define empty lists to store known and other compounds' values
    mg_g_values = {'known': [], 'other': []}
    STD_values = {'known': [], 'other': []}
    
    # Iterate through abrv_dict to get values for known and other compounds
    for key, value in abrv_dict.items():
        for abrv, compound in value.items():
            index = full_compound_list.index(compound)
            mg_g_values[key].append(full_mean_data[index])
            STD_values[key].append(full_sd_data[index])
    
    # # Convert abrv_dict to lists
    # abrv_lists = {'known': list(abrv_dict['known'].keys()), 'other': list(abrv_dict['other'].keys())}

    # Convert abrv_dict to lists
    name_lists = {'known': list(abrv_dict['known'].values()), 'other': list(abrv_dict['other'].values())}
    
    # Set known and other colors and font colors
    colors = {'known': ['#BA55D3', '#6A5ACD', '#9370DB', '#9932CC', '#8B008B'],
              'other': ['#FF8C00', '#FFD700', '#D2B48C', '#2F4F4F', '#008080', '#4682B4', '#0000FF', '#00008B']}
    
    font_colors = {'known': ['white','white','white','white','white'], 
                   'other': ['black','black','black','white','white','white', 'white','white']}
    
    # Get the total sum of mg/g and STD values for known and other compounds
    mg_g_sum = {'known': round(sum(mg_g_values['known']), 1), 'other': round(sum(mg_g_values['other']), 1)}
    STD_sum = {'known': round(sum(STD_values['known']), 1), 'other': round(sum(STD_values['other']), 1)}
    
    # Create final data dataframe with all data
    final_data = pd.DataFrame({
        'Compound_Name': name_lists['known'] + name_lists['other'],
        'mg_g_value': mg_g_values['known'] + mg_g_values['other'],
        'STD_value': STD_values['known'] + STD_values['other'],
        'Legend_Color': colors['known'] + colors['other'],
        'Legend_Font_Color': font_colors['known'] + font_colors['other']},
        columns=['Compound_Name', 'mg_g_value', 'STD_value', 'Legend_Color', 'Legend_Font_Color'])
    
    # Call the graphic and table functions with consolidated inputs
    donut_plot_generator(sample_id, sample_name, abrv_dict, mg_g_values, STD_values, mg_g_sum, STD_sum, colors, font_colors)
    legend_table_generator(sample_id, sample_name, final_data)
    dose_table_generator(sample_id, sample_name, mg_g_sum['known'])
    

def donut_plot_generator(sample_id, sample_name, abrv_dict, mg_g_values, STD_values, mg_g_sum, STD_sum, colors, font_colors):
    """
    Generates the Donut Graphic based on the mean data for sample_id.
    
    Parameters:
    - sample_id: str
        The search term to use when selecting rows.
    - sample_name: str
        The name of the sample.
    - full_compound_list: list
        Full list of all compounds to be represented.           
    - full_mean_data: list
        List containing the mean mg/g data for all compounds.
    - full_sd_data: list
        List containing the standard deviation mg/g data for all compounds.
    
    Returns:
    - Nothing
    """    
    # Create pie chart for known alkaloids
    known_pie = go.Pie(
        labels=list(abrv_dict['known'].keys()),
        values=mg_g_values['known'],
        textposition='inside',
        text=[f'{value}±{STD_values["known"][i]}' for i, value in enumerate(mg_g_values['known'])],
        textfont=dict(size=15, color=font_colors['known']),
        textinfo='text+label',
        hole=.6,
        domain={"x": [0.2, 0.8], "y": [0.1, 0.9]},
        name='Known Entheogenic Alkaloids',
        marker_colors=colors['known'])
    
    # Create pie chart for other alkaloids
    other_pie = go.Pie(
        labels=list(abrv_dict['other'].keys()),
        values=mg_g_values['other'],
        textposition='inside',
        text=[f'{value}±{STD_values["other"][i]}' for i, value in enumerate(mg_g_values['other'])],
        textfont=dict(size=15, color=font_colors['other']),
        textinfo='text+label',
        hole=.75,
        domain={"x": [0.1, 0.9], "y": [0, 1]},
        name='Other Serotonergic Alkaloids',
        marker=dict(line=dict(color='white', width=2)),
        marker_colors=colors['other'])
    
    # Create layout for the chart
    layout = go.Layout(
        title=dict(font=dict(size=50), text=f'{sample_id} {sample_name}<br>CHEMICAL PROFILE'),
        title_x=0.5,
        showlegend=False,
        annotations=[
            dict(text=f'{mg_g_sum["known"]}±{STD_sum["known"]}mg/g', x=0.5, y=0.55, font_size=32, showarrow=False),
            dict(text='Known Entheogenic Alkaloids TOTAL', x=0.5, y=0.50, font_size=13, showarrow=False),
            dict(text=f'{mg_g_sum["other"]}±{STD_sum["other"]}mg/g', x=0.5, y=0.42, font_size=24, showarrow=False),
            dict(text='Other Serotonergic Alkaloids TOTAL', x=0.5, y=0.46, font_size=11, showarrow=False)],
        autosize=False,
        width=800,
        height=800,
        margin=dict(l=0, r=0, b=0, t=150, pad=4))

    # Create figure with the known and other pie charts and the layout
    donut_fig = go.Figure(data=[known_pie, other_pie], layout=layout)
    
    # Display the figure and save it as an SVG image
    #plot(donut_fig)
    donut_output_filename = f'{sample_id}-donut_plot.svg'
    donut_fig.write_image(donut_output_filename)

def legend_table_generator(sample_id, sample_name, final_data):        
    # Filter data to exclude compounds with 0 mg_g value and sort by mg_g value in descending order
    legend_df = final_data[final_data['mg_g_value'] != 0].sort_values('mg_g_value', ascending=False)
    
    # Add column to display mg_g value with its corresponding STD value
    legend_df['mg_g_STD_value'] = legend_df['mg_g_value'].astype(str) + '±' + legend_df['STD_value'].astype(str)
    
    # Define table header and cell formatting
    header = dict(values=['<b>Compound Name<b>', '<b>Replicate AVG±STD<b>'],
                  align='center',
                  fill=dict(color='black'),
                  font=dict(family='Arial', size=20, color='white'))
    cells = dict(values=[[f'<br>{name} (mg/g)' for name in legend_df['Compound_Name']], [f'<br>{value}' for value in legend_df['mg_g_STD_value']]],
                  align=['center', 'center'],
                  line=dict(color='black', width=1),
                  fill=dict(color=[legend_df['Legend_Color'], 'white']),
                  font=dict(family='Arial', size=24, color=[legend_df['Legend_Font_Color'], 'black']),
                  height=50)
    
    # Generate Legend Table
    legend_table = go.Figure(data=[go.Table(header=header, cells=cells)],
                      layout=dict(height=565,
                                  width=493,
                                  autosize=False,
                                  margin=dict(l=0, r=0, b=0, t=0, pad=4),
                                  showlegend=False))
    
    # Display the table and save it as an SVG image
    #plot(legend_table)
    legend_table_output_filename = sample_id + '-legend_table.svg'
    legend_table.write_image(legend_table_output_filename)


# NEEDS BETTER DOCUMENTATION##################################################
def dose_table_generator(sample_id, sample_name, known_mg_g_sum):
    # Define dose information
    dose_fruit_g = [0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]
    dose_active_mg = []
    dose_category = []
    dose_color = []
    dose_font_color = []
    dose_column = []
    
    # Compute dose information
    for fruit_g in dose_fruit_g:
        dose_mg = known_mg_g_sum * fruit_g
        dose_active_mg.append(f'<br><b>{round(dose_mg, 1)}<b>')
        if dose_mg <= 1.5:
            use_category = '<b>Explore<b>'
            use_color = '#ADFF2F'
            font_color = 'black'
        elif dose_mg <= 6.0:
            use_category = '<b>Micro<b>'
            use_color = '#00FF00'
            font_color = 'black'
        elif dose_mg <= 25.0:
            use_category = '<b>Rec/Out<b>'
            use_color = '#00ffff'
            font_color = 'black'
        elif dose_mg <= 40.0:
            use_category = '<b>Therapy<b>'
            use_color = '#0000ff'
            font_color = 'white'
        elif dose_mg <= 50.0:
            use_category = '<b>Spirit<b>'
            use_color = '#9932CC'
            font_color = 'white'
        else:
            use_category = '<b>Deep<b>'
            use_color = '#ff00ff'
            font_color = 'white'
        dose_category.append(use_category)
        dose_color.append(use_color)
        dose_font_color.append(font_color)
        dose_column.append(125)
    
    # Create dose table
    dose_fruit_g = ['Fruit Dose (g)'] + [round(x, 1) for x in dose_fruit_g]
    dose_active_mg = ['<b>Expected Psychoactive Tryptamines (mg)<b>'] + dose_active_mg
    dose_category = ['<b>Recommended Use<b>'] + dose_category
    dose_color = ['black'] + dose_color
    dose_font_color = ['white'] + dose_font_color
    dose_column = [200] + dose_column
    
    # Generate table
    dose_table = go.Figure(data=[go.Table(
        columnwidth=dose_column,
        header=dict(
            values=[f'<br><b>{dose}<b>' for dose in dose_fruit_g],
            align=['right', 'center'],
            fill=dict(color=['black', 'white']),
            line=dict(width=1, color='black'),
            font=dict(family='Arial', size=[20, 25], color=['white', 'black']),
            height=40),
        cells=dict(
            values=list(zip(dose_category, dose_active_mg)),
            align=['left', 'center'],
            line=dict(width=1, color='black'),
            fill=dict(color=dose_color),
            font=dict(family='Arial', size=[15, 25], color=dose_font_color),
            height=50))])
    
    # Update table layout
    dose_table.update_layout(
        width=1250,
        height=250,
        title=dict(text=f"{sample_id} {sample_name}<br>RECOMMENDED DOSAGE CHART"),
        title_x=0.5,
        font=dict(size=18),
        autosize=False,
        margin=dict(l=0, r=0, b=0, t=75, pad=4),
        showlegend=False)

    # Display the table and save it as an SVG image
    #plot(dose_table)
    dose_table_output_filename = sample_id + '-dose_table.svg'
    dose_table.write_image(dose_table_output_filename)


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

###############################################################################
#
# Flush Test Generator
#
###############################################################################
def indiv_flush_table_generator(sample_id, table_colors, font_colors, sample_labels, indiv_flush_df):
    
    table_data_rev = [indiv_flush_df['North-West<br>  '].tolist(),
                  indiv_flush_df['North-East<br>   '].tolist(),
                  indiv_flush_df['Center<br> '].tolist(),
                  indiv_flush_df['South-West<br>     '].tolist(),
                  indiv_flush_df['South-East<br>      '].tolist()]

    # Define header and cells for the table trace
    header = dict(values=['  <b>Flush<br>Position<b>'] + sample_labels,
                  fill=dict(color='black'),
                  align='center',
                  font=dict(size=20, color='white'))

    cells=dict(values=[[f'<b>{row}</b>' for row in indiv_flush_df['Compound'].tolist()]] + table_data_rev,
                fill = dict(color=[table_colors,
                                  ['whitesmoke' for color in table_colors]]),
                line=dict(color='black', width=1),
                align='center',
                font = dict(size=[15,20], color=[font_colors,
                                            ['black' for font_color in font_colors]]))

    # Create table trace
    table_trace = go.Table(
        columnwidth=[575,375],
        header=header,
        cells=cells,)

    indiv_flush_table = go.Figure(data=table_trace)

    indiv_flush_table.update_layout(height=610,
                              width=950,
                              autosize=False,
                              margin=dict(l=0, r=0, b=0, t=0, pad=4),
                              showlegend=False)

    #plot(indiv_flush_table)
    indiv_flush_table_output_filename = f'{sample_id}-indiv_flush_table.svg'
    indiv_flush_table.write_image(indiv_flush_table_output_filename)
    
def indiv_flush_bar_generator(sample_id, sample_cultivar, colors_dict, indiv_flush_df):
    
    df = indiv_flush_df.transpose()
    # set column names from the first row
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)

    mass_labels = [round(mass,2) for mass in df['Sample Mass (g)']]

    location_list = ['North-West', 'North-East', 'Center', 'South-West', 'South-East']
    df['Location'] = location_list
    
    # list of columns to keep
    cols_to_keep = ['Location', 'Sample Mass (g)', 'Psilocybin (mg/g)', 'Psilocin (mg/g)']
    
    # drop columns not in the list
    df = df.drop(columns=[col for col in df.columns if col not in cols_to_keep])
    
    
    # melt the DataFrame
    df_melted = pd.melt(
        df, 
        id_vars=['Location', 'Sample Mass (g)'], 
        var_name='Compound Component', 
        value_name='Concentration (mg/g)')
    df_melted['Location_SampleMass'] = df_melted['Location'].astype(str) + '<br>' + df_melted['Sample Mass (g)'].astype(str) + 'g'

    # create a list of colors based on columns
    use_colors = []
    for col in df_melted['Compound Component']:
        for key, value in colors_dict.items():
            if col.startswith(key):
                use_colors.append(value[0])
                break
            
    # create the bar graph
    indiv_flush_bar_plot = go.Figure(
        data=go.Bar(x=df_melted['Location_SampleMass'] , 
                    y=df_melted['Concentration (mg/g)'], 
                    text=[f'{df_melted["Compound Component"][v].split(" ")[0]}<br>{value}' for v, value in enumerate(df_melted['Concentration (mg/g)'])], 
                    hovertemplate='Location: %{x}<br>' + 
                                  'Compound Component: %{text}<br>' + 
                                  'Concentration: %{y:.2f} mg/g<br>',
                    marker_color=use_colors,
                    textfont=dict(size=10)), 
        layout=go.Layout(
            title='Concentration of Compound Components',
            barmode='group'))
    
    # Update layout for bar graph
    indiv_flush_bar_plot.update_layout(
        title=dict(
            text=f'{sample_name} {sample_cultivar}<br>Position, Mass, PCB+PCN Profile Comparison',
            x=0.5,
            xanchor='center',
            font=dict(size=22)),
        xaxis=dict(title='Flush Test Position',
                   title_font=dict(size=15)),
        yaxis=dict(title='Compound mg/g',
                   title_font=dict(size=15),
                   showticklabels=False),
        barmode='group',
        showlegend=False,
        yaxis_range=[0,20],
        margin = dict(l=10,r=10,t=75,b=10),
        annotations=[dict(text='Recommended Use Ranges:<br>Spiritual+   Therapeutic   Rec/Outdoors  Microdose',
                          x=4.7,
                          y=10.25,
                          font_size=13,
                          textangle=90,                      
                          showarrow=False)])
    #plot(indiv_flush_bar_plot)
    indiv_flush_bar_plot_output_filename = f'{sample_id}-indiv_flush_bar.svg'
    indiv_flush_bar_plot.write_image(indiv_flush_bar_plot_output_filename)

def indiv_flush_test_graphics_generator(sample_id, specific_sample_df, full_compound_list):
    """
    Generates a flush bar graph for a given sample DataFrame and a list of compounds.

    Parameters:
    specific_sample_df (pandas.DataFrame): A DataFrame containing information for a specific sample.
    full_compound_list (list): A list of compound names.

    Returns:
    None

    """
    
    # List of positions for the flush bar
    position_list = ['North-West<br>  ', 'North-East<br>   ', 'Center<br> ', 'South-West<br>     ', 'South-East<br>      ']
    
    # Get sample name and cultivar
    sample_cultivar = specific_sample_df.iloc[0, 6]
    sample_name = specific_sample_df.iloc[0, 1].split(' Position')[0]
    
    
    # Create sample names
    replicate_list = specific_sample_df['Sample_ID']

    replicate_masses = specific_sample_df['Sample_Weight_(g)']
    
    # Create compound names
    table_rows = ['Sample Mass (g)'] + [f'{item} (mg/g)' for item in full_compound_list]
    compounds = full_compound_list
    
    # Create data for each sample
    replicate_data = []
    table_data = []
    
    # Use iterrows() to iterate over the rows of the DataFrame
    for r, row in specific_sample_df.iterrows():
        # Use a list comprehension to select only column names that contain the search string
        columns_to_select = [col for col in row.index if 'mg_g' in col]
        # Use loc[] to select only the columns that contain the search string, and then convert the values to a list
        values = row.loc[columns_to_select].values.tolist()
        # Use sum() to concatenate all the lists of values into one list
        values = [float(value) for value in values]
        table_values = [round(replicate_masses[r], 2)] + [float(value) for value in values]
        replicate_data.append(values)
        table_data.append(table_values)
 
    # Define colors for each compound
    colors_dict = {'Norbaeocystin':['#4682B4'],
                   'Baeocystin':['#2F4F4F'],
                   'Aeruginascin':['#0000FF'],
                   'Psilocybin':['#6A5ACD'],
                   'Adenosine':['#FF8C00'],
                   'Bufotenin':['#9932CC'],
                   '4-HT':['#7AC5CD'],
                   'Cordycepin':['#FFD700'],
                   'Norpsilocin':['#008080'],
                   'Psilocin':['#9370DB'],
                   '4-HTMT':['#00008B'],
                   'Tryptamine':['#D2B48C'],
                   'NN-DMT':['#BA55D3'],
                   '5-MEO-DMT':['#8B008B'],
                   '4-ACO-DMT':['#E0B0FF']}
    colors = list(colors_dict.values())     
    font_colors = ['white']
    for k,key in enumerate(list(colors_dict.keys())):
        if 'Adenosine' in key or 'Cordycepin' in key or 'Tryptamine' in key or 'Four-ACO-DMT' in key:
            colors_dict[key].append('black')
        else:
            colors_dict[key].append('white')
    
    temp_colors = []
    
    sample_labels = [f'{position_list[r]}{replicate}' for r, replicate in enumerate(replicate_list)]
    
    indiv_flush_df = pd.DataFrame(data=table_data)
    indiv_flush_df = indiv_flush_df.transpose()
    indiv_flush_df.columns = position_list


    # insert a new column with the list as data
    indiv_flush_df.insert(loc=0, column='Compound', value=table_rows)

    for key, value in colors_dict.items():
        for item in indiv_flush_df['Compound']:
            if key in item:
                temp_colors.append(value[0])
    # table_colors = ['black'] + temp_colors
    table_colors = ['black'] + [item[0] for item in colors]
    # # Iterate over each row
    # drop_index = []
    # for index, row in indiv_flush_df.iterrows():
    #     row_sum = 0
    #     for col in row:
    #         if isinstance(col, (int, float)):
    #            row_sum = row_sum+col
    #     if row_sum == 0:
    #         drop_index.append(index)    
    # indiv_flush_df = indiv_flush_df.drop(index=drop_index)
    
    # Generate the Individual Flush Table
    indiv_flush_table_generator(sample_id, table_colors, font_colors, sample_labels, indiv_flush_df)
    indiv_flush_bar_generator(sample_id, sample_cultivar, colors_dict, indiv_flush_df)

###############################################################################


def pie_table_generator(ft_start, ft_end, ft_df_raw, shades_of_red):
    # Generate Pie Table
    table_cols = [col.replace('_', ' ') for col in ft_df_raw.columns]
    
    for c, col in enumerate(table_cols):
        if col == 'PCB PCN SUM mg g':
            table_cols[c] = 'PCB+PCN<br>(mg/g)'
        elif col == 'Fruit PCB+PCN mg':
            table_cols[c] = 'Fruit<br>PCB+PCN(mg)'
        elif col == 'Sample Mass g':
            table_cols[c] = 'Sample<br>Mass(g)'
        else:
            table_cols[c] = f'<br>{col}<br>'
    
    # Define header and cells for the table trace
    header = dict(values=table_cols,
                  fill=dict(color='black'),
                  align='center',
                  font=dict(size=14, color='white'),
                  height=50)
    
    cells = dict(values=[ft_df_raw[name] for name in ft_df_raw.columns],
                fill = dict(color=['black',
                                  ['whitesmoke' for color in shades_of_red]]),
                align='center',
                font = dict(size=12, color=['white',
                                              ['black' for color in shades_of_red]]))
    # Create the table
    pie_table = go.Figure(data=[go.Table(
        header = header,
        cells = cells)],)
    pie_table.update_layout(
        width=700,
        height=952,
        margin=dict(l=0,r=0,t=0,b=0))
    #plot(flush_table)
    pie_table_output_filename = f'FT{ft_start}-{ft_end}-pie_table'
    pie_table.write_image(f'{pie_table_output_filename}.svg')


def cat_boost_regressor(ft_df):
    # CatBoostRegressor Training/Testing Process
    # Prepare data for training
    X = ft_df.drop('Fruit_PCB+PCN_mg', axis=1)
    y = ft_df['Fruit_PCB+PCN_mg']
    
    # Split the data into training and testing datasets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42)
    
    # Train a CatBoostRegressor model
    model = CatBoostRegressor(verbose=0)
    model.fit(X, y)
    
    # Get the feature importance scores
    importances = model.feature_importances_
    
    # Get the column names of X_train
    features = X_train.columns
    
    # Create a pandas dataframe to store the feature importance scores
    df_importances = pd.DataFrame({'Analysis Feature': features, '▲-Contribution %': [round(importance, 2) for importance in importances]})
    df_importances = df_importances.sort_values(by='▲-Contribution %', ascending=False)
    
    # Print the top 10 features with the highest importance scores
    print(df_importances.head(10))
    return(df_importances)

def pie_colors_fonts_generator(df_importances):
    reds = cl.scales['9']['seq']['Reds']
    shades_of_red = cl.interp(reds, len(df_importances))
    shades_of_red.reverse()
    if len(shades_of_red) <= 4:
        font_colors = ['white'] * len(shades_of_red)
    else:
        font_colors = ['white' for color in shades_of_red]
        font_colors[4:] = ['black'] * (len(shades_of_red) - 4)
    return(shades_of_red, font_colors)

def flush_pie_generator(ft_start, ft_end, ft_df, descriptor):
    df_importances = cat_boost_regressor(ft_df)
    
    shades_of_red, font_colors = pie_colors_fonts_generator(df_importances)
    
    pie_table_generator(ft_start, ft_end, ft_df_raw, shades_of_red)
    
    # Create the pie chart
    fig1 = go.Figure(data=[go.Pie(labels=df_importances['Analysis Feature'], values=df_importances['▲-Contribution %'], marker_colors=shades_of_red)])
    fig1.update_layout(
        title={
            'text': f'Flush Test {descriptor}Feature Comparison<br>% Effect on PCB+PCN mg/g',
            'y':0.90,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        title_font_size=20,
        width=600,
        height=400,
        margin=dict(l=0,r=0,t=100,b=0))
    
    #plot(fig1)
    if ' ' in descriptor:
        descriptor = descriptor.replace(' ', '_')
    flushpie_output_filename = f'FT{ft_start}-{ft_end}-{descriptor}flushpie'
    fig1.write_image(f'{flushpie_output_filename}.svg')
    return(shades_of_red)

###############################################################################

def mean_df_generator(df, sample_id, sample_name):
    df = df.reset_index()
    df = df.drop(columns=['index'])
    # create a new empty DataFrame with the same columns as the original DataFrame
    mean_df = pd.DataFrame(columns=df.columns)
    # reindex the new DataFrame to set the same column order as the original DataFrame
    mean_df = mean_df.reindex(columns=df.columns)
    # fill the first row with None values
    mean_df.loc[0] = [None] * len(mean_df.columns)
    for c, column in enumerate(df.columns):
        for r, row in df.iterrows():
            value = row[column]
            if r == 0:
                if isinstance(value, str) or column =='Generation_Date' or column =='Date_Processed':
                    string_value = value
                    # Store string_value in first row of mean_df[column]
                    mean_df.iloc[0, c] = string_value
        if df[column].dtype == 'str' or column =='Generation_Date' or column =='Date_Processed':
            pass
        else:
            try:
                df[column]  = df[column].replace('', 0)    
                col_mean = df[column].mean()
                #print(col_mean)
                # Store col_mean in first row of mean_df[column]
                mean_df.iloc[0, c] = col_mean
            except TypeError:
                print(f'TypeError: {column}')    
    mean_df['Sample_ID'] = sample_id
    mean_df['Sample_Name'] = sample_name
    mean_df['Generation_Date'] = df.iloc[0, 7]
    mean_df['Date_Processed'] = df.iloc[0, 8]
    mean_df['Lab_Description'] = df.iloc[0, 14]
    mean_df['Homogenized_Description'] = df.iloc[0, 15]
    return(mean_df)


###############################################################################
#
# MAIN PROCESSING AREA
#
###############################################################################

# Use Python's built-in configparser library to parse the variables in the config.txt file
config = configparser.ConfigParser()
config.read('config.txt')

automation_workspace = config.get('DEFAULT', 'automation_workspace')
template_dir = config.get('DEFAULT', 'template_dir')
service_file_path = config.get('DEFAULT', 'service_file_path')
gsheet_key = config.get('DEFAULT', 'gsheet_key')
sheet_name = config.get('DEFAULT', 'sheet_name')

pio.renderers.default='svg'

# Load Main Dataframe
try:
    print('DATAFRAME LOADED')
    print(loaded_df.head(1))
except NameError:
    print('LOADING DATAFRAME')
    loaded_df, loaded_spreadsheet = load_worksheet_from_gsheet(service_file_path,gsheet_key,sheet_name)

# Create a Copy of the Loaded Dataframe
try:
    print('UPDATED DATAFRAME LOADED')
    print(updated_df.head(1))
except NameError:
    print('UPDATING LOADED DATAFRAME')
    # Save an Arhcive of the Loaded Dataframe
    #save_archive_worksheet(updated_df, loaded_spreadsheet)
    
    # create a duplicate dataframe
    updated_df = loaded_df
    
    # Generate List of All Samples in loaded_df
    sample_list = loaded_df['Sample_ID'].tolist()
    
    # Calculate mg/g values for all Compounds
    for sample in sample_list:
        sample_id = sample
        updated_df = calculate_mg_g_values(updated_df, sample_id)
    
    # Save an Updated Dataframe to the Google Sheet
    # PLACEHOLDER FUNCTION


# # SAMPLE LIST PLACEHOLDER Set Sample ID List to work with
# sample_list = ['HLO126', 'HLO127', 'HLO128', 'HLO129']

# for sample_id in sample_list:

#     # Set Sample ID to work with
#     #sample_id = 'HLO124'
    
#     # Create a new DataFrame containing only the rows where 'Sample_ID' contains the search term
#     specific_sample_df = updated_df[updated_df['Sample_ID'].str.contains(sample_id)].copy()

#     # Generate Stats Dataframe
#     sample_info_df, full_compound_list, full_mean_data, full_sd_data = stats_df_generator(specific_sample_df)
    
#     sample_name = sample_info_df['Sample_Name']
#     report_type = sample_info_df['Report_Type']
    
#     sample_folder = f'{automation_workspace}/{report_type} - {sample_id} - {sample_name}'
    
#     # Check if the folder exists
#     if not os.path.exists(sample_folder):
#         # Create the folder if it doesn't exist
#         os.makedirs(sample_folder)
    
#     # Change the current working directory to the folder
#     os.chdir(sample_folder)
    
#     # Generate Page Topper Table containing Sample ID & Name
#     item_id_table_generator(sample_id, sample_name)
    
#     # Generate Sample Information Table
#     profile_table_generator(sample_id, sample_name, sample_info_df)
    
#     # Generate Donut Graphic, Legend Table, and Dosage Table
#     profile_graphics_generator(sample_id, sample_name, full_compound_list, full_mean_data, full_sd_data)


# Comparing bin vs position vs mass vs flush effects on PCB+PCN mg/g
ft_start = 3

ft_count = ft_start

ft_end = 11

ft_list = []

while ft_count <= ft_end:
    ft_list.append(f'FT{ft_count}')
    ft_count+=1

ft_df = pd.DataFrame(columns=['Sample_ID','Bin_ID','Flush_ID','Position','Sample_Mass_g','PCB_PCN_SUM_mg_g'])

total_df = pd.DataFrame(columns=updated_df.columns)

# Generate Flush Bar Graphic
for ft in ft_list:
    sample_id = ft
    all_sample_df = updated_df[updated_df['Sample_ID'].str.contains(sample_id)].copy()
    replicate_list = all_sample_df['Sample_ID']
    replicate_list = [x for x in replicate_list if '-' not in x and ',' not in x]
    if ft in replicate_list:
        replicate_list.remove(ft)    
    # drop rows where Sample_ID is not in replicate_list
    specific_sample_df = all_sample_df[all_sample_df['Sample_ID'].isin(replicate_list)]
    # Generate Stats Dataframe    
    sample_info_df, full_compound_list, full_mean_data, full_sd_data = stats_df_generator(specific_sample_df)   
    sample_name = sample_info_df['Sample_Name'].split(' Position')[0]
    report_type = sample_info_df['Report_Type']
    sample_cultivar = sample_info_df['Cultivar']
    flush_test_folder = f'{automation_workspace}/Flush - FT{ft_start}-{ft_end} - {sample_cultivar}'
    indiv_flush_folder = f'{flush_test_folder}/{ft}'
    # Check if the folder exists
    try:
        if not os.path.exists(indiv_flush_folder):
            # Create the folder if it doesn't exist
            os.makedirs(indiv_flush_folder)
    except FileExistsError:
        pass
    os.chdir(indiv_flush_folder)    
    # Generate Page Topper Table containing Sample ID & Name
    item_id_table_generator(sample_id, sample_name)
    # Generate Sample Information Table
    profile_table_generator(sample_id, sample_name, sample_info_df)    
    # Generate Donut Graphic, Legend Table, and Dosage Table
    profile_graphics_generator(sample_id, sample_name, full_compound_list, full_mean_data, full_sd_data)
    # Generate Flush Bar Graphic and Legend Table
    indiv_flush_test_graphics_generator(sample_id, specific_sample_df, full_compound_list)   
    position_list = [1, 2, 3, 4, 5] # [NW, NE, C, SW, SE]
    sample_name = [replicate[1]['Sample_Name'] for replicate in specific_sample_df.iterrows()][0].split(' ')
    sample_id = [replicate[1]['Sample_ID'] for replicate in specific_sample_df.iterrows()]
    bin_id = [f'{sample_name[1]}' for position in position_list]
    flush_id = [f'{sample_name[3]}' for position in position_list]  
    pcb_pcn_sum = [round(specific_sample_df.loc[i, 'Psilocybin_mg_g'] + specific_sample_df.loc[i, 'Psilocin_mg_g'],1) for i in specific_sample_df.index]
    sample_mass = [replicate[1]['Sample_Weight_(g)'] for replicate in specific_sample_df.iterrows()]
    fruit_pcb_pcn = [0]*len(pcb_pcn_sum)
    data_dict = {'Sample_ID' : sample_id,
                  'Bin_ID' : bin_id,
                  'Flush_ID' : flush_id,
                  'Position' : position_list,
                  'Sample_Mass_g' : sample_mass,
                  'PCB_PCN_SUM_mg_g' : pcb_pcn_sum,
                  'Fruit_PCB+PCN_mg' : fruit_pcb_pcn}
    df = pd.DataFrame(data=data_dict)    
    data= [ft_df, df]
    ft_df = pd.concat(data)
    total_df = pd.concat([total_df, specific_sample_df])

# Generate Nuanced and Broad Dataframes
# Work on ft_df for graphics/tables
os.chdir(flush_test_folder)    

sample_info_df, full_compound_list, full_mean_data, full_sd_data = stats_df_generator(total_df)    

pre_flush_mean_df = total_df.reset_index().drop(columns=['index'])

sample_id = f'FT{ft_start}-{ft_end}'
sample_name = 'All Flushes Mean'

all_flush_mean_df = mean_df_generator(pre_flush_mean_df, sample_id, sample_name)

sample_info_df, full_compound_list, full_mean_data, full_sd_data = stats_df_generator(all_flush_mean_df)  

# Generate Page Topper Table containing Sample ID & Name
item_id_table_generator(sample_id, sample_name)

# Generate Sample Information Table
profile_table_generator(sample_id, sample_name, sample_info_df)

# Generate Donut Graphic, Legend Table, and Dosage Table
profile_graphics_generator(sample_id, sample_name, full_compound_list, full_mean_data, full_sd_data)


def group_flush_test_graphics_generator(sample_id, df, full_compound_list):
    print('DO GROUP FLUSH TEST GRAPHICS GENERATION')

# Generate Flush Bar Graphic and Legend Table
group_flush_test_graphics_generator(sample_id, specific_sample_df, full_compound_list)   

ft_df = ft_df.reset_index()
ft_df = ft_df.drop(columns=['index'])
for index, row in ft_df.iterrows():
    ft_df.loc[index, 'Fruit_PCB+PCN_mg'] = round(row['Sample_Mass_g'] * row['PCB_PCN_SUM_mg_g'],1)

# Create Pie Graphics
# Remove Blanks from the dataset
ft_df.replace('', np.nan, inplace=True)
ft_df.replace(0, np.nan, inplace=True)
ft_df.dropna(inplace=True)

ft_df_raw = ft_df

ft_df_raw['Sample_Mass_g'] = ft_df_raw['Sample_Mass_g'].round(2)

ft_df = ft_df.drop(columns=['Sample_ID'])

ft_df_nuanced = ft_df

ft_df_nuanced = ft_df_nuanced.drop(columns=['Sample_Mass_g','PCB_PCN_SUM_mg_g'])

# Apply one-hot encoding to the 'Sample_ID' column
ft_df_nuanced = pd.get_dummies(ft_df_nuanced, columns=['Position','Bin_ID','Flush_ID'])

ft_df_dict = {'Nuanced ': ft_df_nuanced,
              'Broad ' : ft_df.drop(columns=['PCB_PCN_SUM_mg_g', 'Sample_Mass_g'])}

# Generate Pie Charts
for key, value in ft_df_dict.items():
    flush_pie_generator(ft_start, ft_end, value, key)


# from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, BayesianRidge
# from sklearn.tree import DecisionTreeRegressor
# from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
# from sklearn.neighbors import KNeighborsRegressor
# from sklearn.svm import SVR
# from xgboost import XGBRegressor
# from lightgbm import LGBMRegressor

# # Define a list of regression models to test
# models = [
#     LinearRegression(),
#     Ridge(),
#     Lasso(),
#     ElasticNet(),
#     DecisionTreeRegressor(),
#     RandomForestRegressor(),
#     GradientBoostingRegressor(),
#     KNeighborsRegressor(),
#     SVR(kernel='linear'),
#     SVR(kernel='poly'),
#     SVR(kernel='rbf'),
#     BayesianRidge(),
#     XGBRegressor(),
#     LGBMRegressor(),
#     CatBoostRegressor(verbose=0)
# ]

# # Define dictionaries to store the MSE and R-squared scores for each model
# mse_scores = {}
# r2_scores = {}

# # Apply one-hot encoding to the 'Sample_ID' column
# ft_df = pd.get_dummies(ft_df, columns=['Bin_ID','Flush_ID'])

# # Train and test each model, and store the scores in the dictionaries
# for model in models:
#     model.fit(X_train, y_train)
#     y_train_pred = model.predict(X_train)
#     y_test_pred = model.predict(X_test)
#     mse_scores[str(model)] = [mean_squared_error(y_train, y_train_pred), mean_squared_error(y_test, y_test_pred)]
#     r2_scores[str(model)] = [r2_score(y_train, y_train_pred), r2_score(y_test, y_test_pred)]

# # Initialize lists to store the model names and scores
# models = []
# train_mse_scores = []
# test_mse_scores = []
# train_r2_scores = []
# test_r2_scores = []

# # Store the model names and scores in the lists
# for model, mse in mse_scores.items():
#     models.append(model)
#     train_mse_scores.append(mse[0])
#     test_mse_scores.append(mse[1])

# for model, r2 in r2_scores.items():
#     train_r2_scores.append(r2[0])
#     test_r2_scores.append(r2[1])

# # Create the dataframe
# model_stats_df = pd.DataFrame({
#     'Model': models,
#     'Train MSE': train_mse_scores,
#     'Test MSE': test_mse_scores,
#     'Train R-squared': train_r2_scores,
#     'Test R-squared': test_r2_scores
# })

# # Print the dataframe
# print(model_stats_df)

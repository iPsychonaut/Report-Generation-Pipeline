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
import configparser
from SVGGenerators import ChemProfGraphGen, ChemProfTableGen, FullFlushPieGen, HeatmapGen, IndivFlushGen
from MLTools import MLFeatureModeling, CatBoostReg 
from PDFGenerators import PDFGen

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
    mean_df = mean_df.assign(
        Sample_ID=pd.Series(sample_id, dtype='object'),
        Sample_Name=pd.Series(sample_name, dtype='object'),
        Generation_Date=pd.Series(df.iloc[0, 7], dtype='object'),
        Date_Processed=pd.Series(df.iloc[0, 8], dtype='object'),
        Lab_Description=pd.Series(df.iloc[0, 14], dtype='object'),
        Homogenized_Description=pd.Series(df.iloc[0, 15], dtype='object'))
    return(mean_df)


###############################################################################
#
# MAIN PROCESSING AREA
#
###############################################################################

# Use Python's built-in configparser library to parse the variables in the config.txt file
config = configparser.ConfigParser()
config.read('C:/Users/theda/OneDrive/Documents/Python/HL/config.txt')

automation_workspace = config.get('DEFAULT', 'automation_workspace')
template_dir = config.get('DEFAULT', 'template_dir')
service_file_path = config.get('DEFAULT', 'service_file_path')
gsheet_key = config.get('DEFAULT', 'gsheet_key')
sheet_name = config.get('DEFAULT', 'sheet_name')


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


# SAMPLE LIST PLACEHOLDER Set Sample ID List to work with
sample_list = ['HLO126', 'HLO127', 'HLO128', 'HLO129']

for sample_id in sample_list:

    # Set Sample ID to work with
    #sample_id = 'HLO124'
    
    # Create a new DataFrame containing only the rows where 'Sample_ID' contains the search term
    specific_sample_df = updated_df[updated_df['Sample_ID'].str.contains(sample_id)].copy()

    # Generate Stats Dataframe
    sample_info_df, full_compound_list, full_mean_data, full_sd_data = stats_df_generator(specific_sample_df)
    
    sample_name = sample_info_df['Sample_Name']
    report_type = sample_info_df['Report_Type']
    
    sample_folder = f'{automation_workspace}/{report_type} - {sample_id} - {sample_name}'
    
    # Check if the folder exists
    if not os.path.exists(sample_folder):
        # Create the folder if it doesn't exist
        os.makedirs(sample_folder)
    
    # Change the current working directory to the folder
    os.chdir(sample_folder)
    
    # Generate Page Topper Table containing Sample ID & Name
    ChemProfTableGen.item_id_table_generator(sample_id, sample_name)
    
    # Generate Sample Information Table
    ChemProfTableGen.profile_table_generator(sample_id, sample_name, sample_info_df)
    
    # Generate Donut Graphic, Legend Table, and Dosage Table
    ChemProfGraphGen.profile_graphics_generator(sample_id, sample_name, full_compound_list, full_mean_data, full_sd_data)


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
    ChemProfTableGen.item_id_table_generator(sample_id, sample_name)
    # Generate Sample Information Table
    ChemProfTableGen.profile_table_generator(sample_id, sample_name, sample_info_df)    
    # Generate Donut Graphic, Legend Table, and Dosage Table
    ChemProfGraphGen. profile_graphics_generator(sample_id, sample_name, full_compound_list, full_mean_data, full_sd_data)
    # Generate Flush Bar Graphic and Legend Table
    IndivFlushGen.indiv_flush_test_graphics_generator(sample_id, specific_sample_df, full_compound_list)   
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
ChemProfTableGen.item_id_table_generator(sample_id, sample_name)
# Generate Sample Information Table
ChemProfTableGen.profile_table_generator(sample_id, sample_name, sample_info_df)    
# Generate Donut Graphic, Legend Table, and Dosage Table
ChemProfGraphGen. profile_graphics_generator(sample_id, sample_name, full_compound_list, full_mean_data, full_sd_data)
# Generate Nuanced and Broad Flush Pies and Table
FullFlushPieGen.broad_nuanced_pie_generator(ft_start, ft_end, ft_df)



def group_flush_test_graphics_generator(sample_id, df, full_compound_list):
    print('DO GROUP FLUSH TEST GRAPHICS GENERATION')

# Generate Flush Bar Graphic and Legend Table
group_flush_test_graphics_generator(sample_id, specific_sample_df, full_compound_list)   


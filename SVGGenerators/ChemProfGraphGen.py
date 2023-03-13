# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 12:09:24 2023

@author: theda
"""
import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import plot
import pandas as pd

pio.renderers.default='svg'

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
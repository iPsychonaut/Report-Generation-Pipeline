# -*- coding: utf-8 -*-

import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import plot
import pandas as pd

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
    
def indiv_flush_bar_generator(sample_id, sample_name, sample_cultivar, colors_dict, indiv_flush_df):
    
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
    indiv_flush_bar_generator(sample_id, sample_name, sample_cultivar, colors_dict, indiv_flush_df)
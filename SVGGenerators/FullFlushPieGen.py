import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import plot
import pandas as pd
from MLTools import CatBoostReg
import pandas as pd
import colorlover as cl
import numpy as np

pio.renderers.default='svg'

def pie_table_generator(ft_start, ft_end, ft_df, shades_of_red):
    
    # Generate Pie Table
    table_cols = [col.replace('_', ' ') for col in ft_df.columns]
    
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
    
    cells = dict(values=[ft_df[name] for name in ft_df.columns],
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


def broad_nuanced_pie_generator(ft_start, ft_end, ft_df):
    ft_df = ft_df.reset_index()
    ft_df = ft_df.drop(columns=['index'])
    for index, row in ft_df.iterrows():
        ft_df.loc[index, 'Fruit_PCB+PCN_mg'] = round(row['Sample_Mass_g'] * row['PCB_PCN_SUM_mg_g'],1)

    # Create Pie Graphics
    # Remove Blanks from the dataset
    ft_df.replace('', np.nan, inplace=True)
    ft_df.replace(0, np.nan, inplace=True)
    ft_df.dropna(inplace=True)


    ft_df = ft_df.drop(columns=['Sample_ID'])
    
    ft_df['Sample_Mass_g'] = ft_df['Sample_Mass_g'].round(2)

    ft_df_nuanced = ft_df

    ft_df_nuanced = ft_df_nuanced.drop(columns=['Sample_Mass_g','PCB_PCN_SUM_mg_g'])

    # Apply one-hot encoding to the 'Sample_ID' column
    ft_df_nuanced = pd.get_dummies(ft_df_nuanced, columns=['Position','Bin_ID','Flush_ID'])

    ft_df_dict = {'Nuanced ': ft_df_nuanced,
                  'Broad ' : ft_df.drop(columns=['PCB_PCN_SUM_mg_g', 'Sample_Mass_g'])}

    # Generate Pie Charts
    for key, value in ft_df_dict.items():
        flush_pie_generator(ft_start, ft_end, value, key)

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
            
    df_importances = CatBoostReg.cat_boost_regressor(ft_df)
    
    shades_of_red, font_colors = pie_colors_fonts_generator(df_importances)
    
    pie_table_generator(ft_start, ft_end, ft_df, shades_of_red)
    
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
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 11:06:52 2023

@author: theda
"""

import plotly 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from plotly.offline import plot

pio.renderers.default='svg'

sample_id = 'TEST003'
sample_name = 'Bin 0 Flush 0'

pcb_pcn_plot_type = 'pcb-pcn'
pcb_pcn_colors = 'Reds'
pcb_pcn_raw_data = [1.5,1.5,1.6,1.4,1.1] # [SW, SE, C, NW, NE]

if len(pcb_pcn_raw_data) == 5:
    s_pos = round((pcb_pcn_raw_data[0]+pcb_pcn_raw_data[1]+pcb_pcn_raw_data[2])/3, 1)
    e_pos = round((pcb_pcn_raw_data[0]+pcb_pcn_raw_data[2]+pcb_pcn_raw_data[3])/3, 1)
    w_pos = round((pcb_pcn_raw_data[1]+pcb_pcn_raw_data[2]+pcb_pcn_raw_data[4])/3, 1)
    n_pos = round((pcb_pcn_raw_data[2]+pcb_pcn_raw_data[3]+pcb_pcn_raw_data[4])/3, 1)
    pcb_pcn_input_data = [[pcb_pcn_raw_data[0], s_pos, pcb_pcn_raw_data[1]],
                          [e_pos, pcb_pcn_raw_data[2], w_pos],
                          [pcb_pcn_raw_data[3], n_pos, pcb_pcn_raw_data[4]]]
else:
    print(f'Data does not meet 5-Position EXACT requirement: {len(pcb_pcn_raw_data)} submitted -> {pcb_pcn_raw_data}')
    


def heatmap_plot_generator(sample_id, sample_name, plot_type, input_data, input_colors):
    if plot_type == 'pcb-pcn':
        font_color='white'
        title_text = 'PCB+PCN (mg/g)'
    elif plot_type == 'sample-mass':
        font_color='black'
        title_text = 'Sample Mass (g)'
    elif plot_type == 'sample-ppm':
        font_color='black'
        title_text = 'Sample ppm'
    
    heatmap_plot = go.Figure(data=go.Heatmap(z=input_data,
                                             colorscale=input_colors,
                                             text=input_data,
                                             textfont=dict(color='black')))
    
    annotations=[]
    
    direct_annot_dict= {'NORTH' : [1, 2.4, 0],
                        'SOUTH' : [1, -0.4, 0],
                        'EAST' : [-0.4, 1, 270],
                        'WEST' : [2.4, 1, 90]}
    
    for key, value in direct_annot_dict.items():
        annotations.append(
            go.layout.Annotation(
                x=value[0],
                y=value[1],
                text=key,
                showarrow=False,
                font=dict(size = 20, color = font_color),
                textangle = value[2]))
    
    for i in range(len(input_data)):
        for j in range(len(input_data[i])):
            annotations.append(
                go.layout.Annotation(
                    x=j,
                    y=i,
                    text=str(input_data[i][j]),
                    showarrow=False,
                    font=dict(size=20, color=font_color),
                    xref='x1',
                    yref='y1',
                    xanchor='center',
                    yanchor='middle'))
    
    
    heatmap_plot.update_layout(title=dict(font=dict(size=23),
                                          x=0.5,
                                          y=0.945,
                                          text=f'{sample_id} {sample_name}<br>{title_text} HEATMAP'),
                               height=480,
                               width=480,
                               margin=dict(l=10, r=10, t=65, b=10, pad=0),
                               annotations=annotations,
                               showlegend=False)
    
    heatmap_plot.update_xaxes(showticklabels=False, showgrid=False)
    heatmap_plot.update_yaxes(showticklabels=False, showgrid=False)
    heatmap_plot.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    plot(heatmap_plot)
    
    heatmap_plot_output_filename = f"{sample_id}-{plot_type}-heatmap_plot.svg"
    heatmap_plot.write_image(heatmap_plot_output_filename)
    
heatmap_plot_generator(sample_id, sample_name, pcb_pcn_plot_type, pcb_pcn_input_data, pcb_pcn_colors)

sample_mass_plot_type = 'sample-mass'
sample_mass_colors = 'Blues'
sample_mass_raw_data = [0.73,0.71,0.78,1.04,1.01] # [SW, SE, C, NW, NE]

if len(sample_mass_raw_data) == 5:
    s_pos = round((sample_mass_raw_data[0]+sample_mass_raw_data[1]+sample_mass_raw_data[2])/3, 1)
    e_pos = round((sample_mass_raw_data[0]+sample_mass_raw_data[2]+sample_mass_raw_data[3])/3, 1)
    w_pos = round((sample_mass_raw_data[1]+sample_mass_raw_data[2]+sample_mass_raw_data[4])/3, 1)
    n_pos = round((sample_mass_raw_data[2]+sample_mass_raw_data[3]+sample_mass_raw_data[4])/3, 1)
    sample_mass_input_data = [[sample_mass_raw_data[0], s_pos, sample_mass_raw_data[1]],
                          [e_pos, sample_mass_raw_data[2], w_pos],
                          [sample_mass_raw_data[3], n_pos, sample_mass_raw_data[4]]]
else:
    print(f'Data does not meet 5-Position EXACT requirement: {len(sample_mass_raw_data)} submitted -> {sample_mass_raw_data}')
    
heatmap_plot_generator(sample_id, sample_name, sample_mass_plot_type, sample_mass_input_data, sample_mass_colors)


sample_ppm_plot_type = 'sample-ppm'
sample_ppm_colors = 'Greens'
sample_ppm_raw_data = [0.73,0.71,0.78,1.04,1.01] # [SW, SE, C, NW, NE]

if len(sample_ppm_raw_data) == 5:
    s_pos = round((sample_ppm_raw_data[0]+sample_ppm_raw_data[1]+sample_ppm_raw_data[2])/3, 1)
    e_pos = round((sample_ppm_raw_data[0]+sample_ppm_raw_data[2]+sample_ppm_raw_data[3])/3, 1)
    w_pos = round((sample_ppm_raw_data[1]+sample_ppm_raw_data[2]+sample_ppm_raw_data[4])/3, 1)
    n_pos = round((sample_ppm_raw_data[2]+sample_ppm_raw_data[3]+sample_ppm_raw_data[4])/3, 1)
    sample_ppm_input_data = [[sample_ppm_raw_data[0], s_pos, sample_ppm_raw_data[1]],
                          [e_pos, sample_ppm_raw_data[2], w_pos],
                          [sample_ppm_raw_data[3], n_pos, sample_ppm_raw_data[4]]]
else:
    print(f'Data does not meet 5-Position EXACT requirement: {len(sample_ppm_raw_data)} submitted -> {sample_ppm_raw_data}')
    
heatmap_plot_generator(sample_id, sample_name, sample_ppm_plot_type, sample_ppm_input_data, sample_ppm_colors)
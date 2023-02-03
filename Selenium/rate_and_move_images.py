# finding files
import glob

# moving files
import shutil

# info about displaying images in plotly
# https://github.com/plotly/dash/issues/71
import dash
from dash import dcc, html, Input, Output, callback_context
import base64

# adding some probabilities to script
import random

import dash_bootstrap_components as dbc

# set the path
general_path = 'InsertYourPathHere'

path = general_path + '/duplicate_check'


# set training, validation and testing path
train = general_path+'/train'
validation = general_path + '/validation'
test = general_path + '/test'


# getting the list of images
jpg_files = glob.glob(path+'/*.jpg')

print(f'this is the amount of images: {len(jpg_files)}')

## start dash ###

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.layout = html.Div([

    # rendered image
    html.Img(id='image'),
    html.Div([
        # margin creates some horizontal distance
        # as in here: https://community.plotly.com/t/horizontally-stack-components/10806/6
        html.Button('Like', id='btn-like', n_clicks=0,style={'background-color': 'green',
                    'color': 'white','width': '40%','display': 'inline-block',"margin-right": "100px"}),
        html.Button('Dislike', id='btn-dislike', n_clicks=0,style={'background-color': 'red',
                    'color': 'white','width': '40%','display': 'inline-block',"margin-bottom": "50px"}),
        html.Div(id='container-button-timestamp')
        ])
])

n = 5

print(f'this is first {n} items of our jpg files list: \n {jpg_files[:n]}')

@app.callback(
    Output('container-button-timestamp', 'children'),
    dash.dependencies.Output('image','src'),
    Input('btn-like', 'n_clicks'),
    Input('btn-dislike', 'n_clicks'),
)
def displayClick(n_clicks, n_clicks_dislike):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    total_clicks = n_clicks + n_clicks_dislike

    random_number_iteration = random.random()
    print(f'our random number is {random_number_iteration}')

    move_message = f'file {jpg_files[total_clicks-1]} was moved to'
    click_message = f'button was most recently clicked and we have total clicks of {total_clicks}. \n'+\
            f'Remaining images: {len(jpg_files)-total_clicks}'

    if 'btn-like' in changed_id:

        suffix = '/like'

        # move picture to like pics, 70% proba to train, 15% to validation and 15% to test data
        if random_number_iteration < 0.7:
            # moving files with shutil https://linuxhint.com/move-file-to-other-directory-python/

            shutil.move(jpg_files[total_clicks-1],train+suffix)
            move_message_feedback = move_message + 'training set'


        elif random_number_iteration < 0.85:

            shutil.move(jpg_files[total_clicks-1],validation+suffix)
            move_message_feedback = move_message + 'validation set'

        else:

            shutil.move(jpg_files[total_clicks-1],test+suffix)
            move_message_feedback = move_message + 'test set'

        click_message_feedback = 'Like ' + click_message

        
    elif 'btn-dislike' in changed_id:

        suffix = '/dislike'

        # move picture to dislike pics, 70% proba to train, 15% to validation and 15% to test data
        if random_number_iteration < 0.7:

            shutil.move(jpg_files[total_clicks-1],train+suffix)
            move_message_feedback = f'file {jpg_files[total_clicks-1]} was moved to training set'
            

        elif random_number_iteration < 0.85:

            shutil.move(jpg_files[total_clicks-1],validation+suffix)
            move_message_feedback = f'file {jpg_files[total_clicks-1]} was moved to validation set'
            

        else:

            shutil.move(jpg_files[total_clicks-1],test+suffix)
            move_message_feedback = f'file {jpg_files[total_clicks-1]} was moved to test set'
            
        click_message_feedback = 'Dislike ' + click_message

    else:
        click_message_feedback = f'None of the images have been rated yet and we have {total_clicks} total clicks. \n'+\
            f'Remaining images: {len(jpg_files)-total_clicks}'
        move_message_feedback = None
    
    if move_message_feedback:
        print(move_message_feedback)

    # adjust image
    print(f'current image_path = {jpg_files[total_clicks]}')
    encoded_image = base64.b64encode(open(jpg_files[total_clicks], 'rb').read())

    return html.Div(click_message_feedback), f'data:image/png;base64,{encoded_image.decode()}'


if __name__ == '__main__':
    app.run_server(debug=True)#, port=8053, host='0.0.0.0')


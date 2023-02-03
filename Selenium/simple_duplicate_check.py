import os
from difPy import dif


def check_for_duplicate_images(path):

    """Deletes duplicate images from given path
    
    Arguments:
    path                (string): the path where to search for duplicate(s)
    
    Returns:
    found_duplicates    (list):  filenames of found duplicate(s)
    """

    search = dif(path)

    results = search.result

    found_duplicates = results.keys()

    delete_duplicates = input(f'Do you want to delete the following {len(found_duplicates)} found duplicates: \n {found_duplicates}\n y/n?\n')

    if delete_duplicates == 'y':
        try:
            
            key_duplicates = [results[key]['location'] for key in found_duplicates]

            print(f'These are the duplicate files: {key_duplicates}')

            for duplicate_file in key_duplicates:
                # Delete the file
                os.remove(duplicate_file)
                
            print(f'We have removed {len(key_duplicates)} duplicate files')

        except:
            raise ValueError('Duplicate deletion did not work')
        

    else:
        print('nothing was deleted')
    
    return found_duplicates
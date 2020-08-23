import os
import pandas as pd
import pickle

for csv in os.listdir('./dataset'):
    motion = csv.split('.')[0]

    data = pd.read_csv('./dataset/' + csv)

    print (f"\nLoad {motion} !\n")

    motion_dir = os.path.join('./dataset', motion)
    
    os.mkdir(motion_dir + '/')

    for i in range(len(data)):
        line = data.loc[i, :]
        file_name = os.path.join(motion_dir, f'{i:05}.txt') 
        
        with open(file_name, 'w') as f:
            for j in range(17):
                col = j*6
                f.write(f'{line[col + 0]} {line[col+1]} {line[col+2]} {line[col+3]} {line[col+4]} {line[col+5]}')


    print ("Finish!")

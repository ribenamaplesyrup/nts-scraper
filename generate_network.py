import pandas as pd
import json
import sys

def shared_music(mixes: "list of csv files"):
    # returns dataframe of tracks from labels played on multiple input shows 
    mix_titles = []
    mixes_df = []
    for mix in mixes:
        df = pd.read_csv(mix)
        mixes_df.append(df)
        mix_titles += [df["mix"][0]]
    df = pd.concat(mixes_df)
    shared_labels = []
    for i,mix in enumerate(mix_titles):
        for j in range(i+1, len(mix_titles)):
            shared_labels += pd.Series(list(set(df.loc[df['mix'] == mix_titles[i]]['label']).intersection(set(df.loc[df['mix'] == mix_titles[j]]['label'])))).tolist()
            print("Found shared labels for " + mix_titles[i] + " and " + mix_titles[j] )
    shared_labels = list(dict.fromkeys(shared_labels))
    shared_labels = [label for label in shared_labels if isinstance(label, str)]
    df = df[df['label'].isin(shared_labels)].reset_index(drop=True)
    df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
    return df

def generate_network(df: "pandas dataframe"):
    # returns nodes and links between shows as dict for input dataframe containing multiple shows
    network = {"nodes":[],"links":[]}
    for mix in df['mix'].unique():
        network["nodes"] += [{"id": mix + " [Show]", "group": 1}]
    for index, row in df.iterrows():
        network['nodes'] += [{'id': row['artist'], 'group': 2},{'id': row['label'], 'group': 3}]
        # could check for duplicates to improve json readability:
        network['links'] += [{'source': row['artist'], 'target': row['label'], 'value': "1"},
                             {'source': row['artist'], 'target': row['mix'] + " [Show]", 'value': "1"}]
    # remove duplicate nodes
    network['nodes'] = [dict(t) for t in {tuple(node.items()) for node in network['nodes']}]
    return network

def main(mixes: "list of csv file locations"):
    # takes a list of shows (in csv format), returns nodes and links in JSON
    df = shared_music(mixes)
    network = generate_network(df)
    with open('network.json', 'w') as fp:
        json.dump(network, fp)

if __name__ == "__main__":
    main(sys.argv[1:])

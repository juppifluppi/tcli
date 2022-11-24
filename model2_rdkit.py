from rdkit import Chem
from rdkit.Chem import Draw
from scopy.ScoPretreat import pretreat
import scopy.ScoDruglikeness
from dimorphite_dl import DimorphiteDL
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rdkit import DataStructs
from rdkit.Chem.Fingerprints import FingerprintMols

df  = pd.read_csv("trainvalues.csv")
x = df['rd_logD']
y = df['rd_MR']

df2  = pd.read_csv("testvalues.csv")
x2 = df2['rd_logD']
y2 = df2['rd_MR']

# read and Conconate the csv's
df_1 = pd.read_csv('first.csv')
df_2 = pd.read_csv('second.csv')
df_3 = pd.concat([df_1, df_2])

# proof and make a list of SMILES
df_smiles = df_3['smiles']
c_smiles = []
for ds in df_smiles:
    try:
        cs = Chem.CanonSmiles(ds)
        c_smiles.append(cs)
    except:
        print('Invalid SMILES:', ds)
print()

# make a list of mols
ms = [Chem.MolFromSmiles(x) for x in c_smiles]

# make a list of fingerprints (fp)
fps = [FingerprintMols.FingerprintMol(x) for x in ms]

# the list for the dataframe
qu, ta, sim = [], [], []

# compare all fp pairwise without duplicates
for n in range(len(fps)-1): # -1 so the last fp will not be used
    s = DataStructs.BulkTanimotoSimilarity(fps[n], fps[n+1:]) # +1 compare with the next to the last fp
    print(c_smiles[n], c_smiles[n+1:]) # witch mol is compared with what group
    # collect the SMILES and values
    for m in range(len(s)):
        qu.append(c_smiles[n])
        ta.append(c_smiles[n+1:][m])
        sim.append(s[m])
print()

# build the dataframe and sort it
d = {'query':qu, 'target':ta, 'Similarity':sim}
df_final = pd.DataFrame(data=d)
df_final = df_final.sort_values('Similarity', ascending=False)
print(df_final)

st.header('TC/L interaction probability model')
st.caption("""Input a SMILES code of your molecule of choice (use e.g. https://pubchem.ncbi.nlm.nih.gov/edit3/index.html).
A probability for interaction with taurocholate/lecithin is computed for the compound at pH 6.5, based on two descriptors: logD and CrippenMR.
The model is based on Mol. Pharmaceutics 2022, 19, 2868−2876 (https://doi.org/10.1021/acs.molpharmaceut.2c00227),
but descriptors are computed via rdkit/scopy instead of MOE/PaDEL, and logD for pH 7.4 instead of 7.0 is used.""")

try:

    SMI = st.text_input('Enter SMILES of drug molecule', 'CC(C)NCC(COC1=CC=C(C=C1)CCOC)O')
    
    dimorphite_dl = DimorphiteDL(
        min_ph = 6.4,
        max_ph = 6.6,
        max_variants = 1,
        label_states = False,
        pka_precision = 0.1
    )
    SMI = str(dimorphite_dl.protonate(SMI)[0])
    
    mol = Chem.MolFromSmiles(SMI)
    sdm = pretreat.StandardizeMol()
    mol = sdm.disconnect_metals(mol)
    
    m = Chem.MolFromSmiles(SMI)
    im = Draw.MolToImage(m)
    
    logd = scopy.ScoDruglikeness.molproperty.CalculateLogD(mol)
    mr = scopy.ScoDruglikeness.molproperty.CalculateMolMR(mol)
    
    tcl1 = ( ( logd - 1.510648) / 1.708574 ) * 1.706694
    tcl2 = ( ( mr - 90.62889 ) / 35.36033 ) * 2.4925333
    
    tcl3 = 1 / ( 1 + ( 2.718281828459045 ** ( -1 * ( 0.9872289 + tcl1 + tcl2 ) ) ) )
    
    st.image(im)
    st.text("logD: " + str(round(logd,2)))
    st.text("CrippenMR: " + str(round(mr,2)))
    st.text("TC/L interaction probability: " + str(round(tcl3,2)))

except:
    pass
    
fig=plt.figure()
ax=fig.add_axes([0,0,1,1])
ax.scatter(x, y, color='b',alpha=0.5)
ax.scatter(x2, y2, color='r',alpha=0.5)
ax.scatter(logd, mr, color='g',alpha=1)
ax.set_xlabel('logD')
ax.set_ylabel('CrippenMR')
ax.set_title('Compound vs. modeling set')

l=ax.scatter(x, y, color='b',alpha=0.5)
p=ax.scatter(x2, y2, color='r',alpha=0.5)
o=ax.scatter(logd, mr, color='g',alpha=1)
ax.legend((l,p,o),("Training set", "Validation set", "Compound"))
plt.show()

st.pyplot(fig)
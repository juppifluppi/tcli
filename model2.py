from rdkit import Chem
from rdkit.Chem import Draw
from scopy.ScoPretreat import pretreat
import scopy.ScoDruglikeness
from dimorphite_dl import DimorphiteDL
import streamlit as st

st.header('TC/L interaction probability model')
st.caption("""Input a SMILES code of your molecule of choice (use e.g. https://pubchem.ncbi.nlm.nih.gov/edit3/index.html).
A probability for interaction with taurocholate/lecithin is computed for the compound at pH 6.5, based on two descriptors: logD and CrippenMR.
The model is based on Mol. Pharmaceutics 2022, 19, 2868−2876 (https://doi.org/10.1021/acs.molpharmaceut.2c00227),
but descriptors are computed via rdkit/scopy instead of MOE/PaDEL, and logD for pH 7.4 instead of 7.0 is used.""")

try:

    SMI = st.text_input('Enter Canonical SMILES of drug molecule', 'CC(C)NCC(COC1=CC=C(C=C1)CCOC)O')
    
    dimorphite_dl = DimorphiteDL(
        min_ph=6.4,
        max_ph=6.6,
        max_variants=1,
        label_states=False,
        pka_precision=0.1
    )
    SMI = str(dimorphite_dl.protonate(SMI)[0])
    
    mol = Chem.MolFromSmiles(SMI)
    sdm = pretreat.StandardizeMol()
    mol = sdm.disconnect_metals(mol)
    
    m = Chem.MolFromSmiles(SMI)
    im=Draw.MolToImage(m)
    
    logd = scopy.ScoDruglikeness.molproperty.CalculateLogD(mol)
    mr = scopy.ScoDruglikeness.molproperty.CalculateMolMR(mol)
    
    tcl1 = ( ( logd - 2.009365 ) / 1.878026 ) * 1.1626256
    tcl2 = ( ( mr - 90.80861 ) / 35.30108 ) * 1.9764294
    
    tcl3 = 1 / ( 1 + ( 2.718281828459045 ** ( -1 * ( 0.7999132 + tcl1 + tcl2 ) ) ) )
    
    st.image(im)
    st.text("logD: " + str(round(logd,2)))
    st.text("CrippenMR: " + str(round(mr,2)))
    st.text("TC/L interaction probability: " + str(round(tcl3,2)))

except:
    pass
    

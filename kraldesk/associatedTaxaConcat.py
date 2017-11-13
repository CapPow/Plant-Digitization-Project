def associatedTaxaConcat(index,record):

#This uses Pandas Groupby Function to lump all records with the same site Number togeather, which also have unique scientificNames
    siteGroups = (recordDF.groupby('siteNum')['scientificName'].unique()) 

    assTaxaGroup = (siteGroups.get(record['siteNum']).tolist()) #Add each record in the group to a list

    #List comprehension for sorting (alphabetically) the list according to scientific names
    assTaxaGroup = sorted([str(item.rstrip()) for item in assTaxaGroup if not (pd.isnull(item) or item is record['scientificName'])])

    if len(assTaxaGroup) > 0: #are there any other taxa found at this site?
        existingAssTaxa = ', ' + record['associatedTaxa'] #if so, join them into a string
        
    else:
        existingAssTaxa = record['associatedTaxa'] #if not, don't include them.
    assTaxaStr = (', '.join(assTaxaGroup) + str(existingAssTaxa)) #either way, join the user entered stuff to the generated lists
    if not assTaxaStr == 'nan':  #I don't know why, sometimes a 'nan' slips through, so I'm checking for it before updating cell.
        recordCell(index,'associatedTaxa',assTaxaStr) #Helper function to update the cell. with new string.

def recordCell(row,col,val):
    recordDF.set_value(row,col,val)

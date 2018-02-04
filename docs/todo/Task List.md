Priority Tasks:

~~-Convert existing, old site / specimen read methods to use the newer easier site# specimen# fields.~~
-Associated Taxa is not being added when processing.
      -Associated Taxa should be a string of scientific names, without authorities generated from joining:
            -a set() datatype containing the list of split(',') associatedTaxa (field entered) from each specimen which shares a site#
            -a set() datatype containing the scientificName from each specimen which shares a site# and is not listed in the set above.
            -Final Associated Taxa string should keep associatedTaxa set before scientificName set (so generated follows user entered).
~~-Remove user dialog when authority is filling in a blank field~~
~~-Remove user dialog (and 'pass') if sciname / authority are the same as proposed change. (It currently ALWAYS asks)~~
-Modify Pandastables preferences windows to load preferences on start up, and save when they are modified.
      -Values to save in preferences:
            -Window Size
            -Collection name
            -Determined by & Date preferences
                  -Should this be an option to automatically append when the sci-name field is entered?
            -Catalog number Prefix, Digits and Start (aka: barcode number)
                  -Possibly add consider dialog at the time of label printing
            -Paths to input field-number-named images and output catalog-number-named images.

Tasks:

-Impliment the rename and move image handling functions from fieldImageHandling.py, possibly at the time of label printing
-Split record processing into: process locality, process names / associated taxa
-Add print label options, and store them in preferences window:
      -Impliment multiple common label dimention presets for use in printLabels.py
      -Include, exclude occurenceRemarks, locationRemarks fields
      -Add print duplicate label Quantity Spinbox widget to specimen rows
-Colorcode Site/Specimen records
-Disable Editing of specific fields (auto generated site#, specimen#)
-Define process when: user edits site records. Should the changes propigate down to specimens from that site, prohibit changes, etc?
-Add generate otherCatalogNumbers ('field numbers') option if importing without them.
-Add some "New blank"-ish option to generate a blank worksheet in appropriate format for those building from scratch.
-Add New site# button to bottom of table. Unlike new specimen, this duplicates nothing.


Future Tasks:
-Site/Specimen Photo from mobile bundling & deliver method
-Submit to portal from within program
      -Final decision on process for importing before mounting
      -Current plan is to treat list it as an observation or use specialized "processing step" tag
      -Explore options for Symbiota image processing script to switch observation processing step tag to vouchered specimen tag
-Generate master list from multiple csv files.
      -This would be useful in a lab senerio where a curator is joining multiple student's collection files.

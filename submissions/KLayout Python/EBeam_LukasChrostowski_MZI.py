'''
--- Simple MZI ---

by Lukas Chrostowski, 2020-2023

Example simple script to
 - create a new layout with a top cell
 - create an MZI
 - take a picture (PNG file)
 - export to OASIS for submission to fabrication

using SiEPIC-Tools functions introduced in ~ v0.3.70, 
specifically connect_pins_with_waveguide and connect_cell

usage:
 - run this script
'''

if SiEPIC.__version__ < '0.3.70':
  pya.MessageBox.warning("Errors", "This example requires SiEPIC-Tools version 0.3.70 or greater.", pya.MessageBox.Ok)

'''
Create a new layout using the EBeam technology,
with a top cell
'''
tech_name = 'EBeam'
mw = pya.Application().instance().main_window()
ly = mw.create_layout(tech_name, 1).layout()
cell = ly.create_cell('top')
lv = mw.current_view()
lv.select_cell(cell.cell_index(), 0)
dbu = ly.dbu
from SiEPIC.utils import get_technology_by_name
TECHNOLOGY = get_technology_by_name(tech_name)

from SiEPIC.scripts import connect_pins_with_waveguide, connect_cell
waveguide_type='Strip TE 1550 nm, w=500 nm'

# Load cells from library
cell_ebeam_gc = ly.create_cell('ebeam_gc_te1550', tech_name)
cell_ebeam_y = ly.create_cell('ebeam_y_1550', tech_name)
cell_ebeam_y_dream = ly.create_cell('ebeam_dream_splitter_1x2_te1550_BB', 'EBeam-Dream', {})

# create a floor plan
fpLayerN = cell.layout().layer(TECHNOLOGY['FloorPlan'])
cell.shapes(fpLayerN).insert(Box(0,0, 605/dbu, 410/dbu))

# grating couplers, place at absolute positions
x,y = 35000, 15000
t = pya.Trans.from_s('r0 %s,%s' % (x,y))
instGC1 = cell.insert(pya.CellInstArray(cell_ebeam_gc.cell_index(), t))
t = pya.Trans.from_s('r0 %s,%s' % (x,y+127000))
instGC2 = cell.insert(pya.CellInstArray(cell_ebeam_gc.cell_index(), t))

# automated test label
text = pya.Text ("opt_in_TE_1550_device_MZI_script", t)
cell.shapes(ly.layer(TECHNOLOGY['Text'])).insert(text).text_size = 5/dbu

# Y branches:
# Version 1: place it at an absolute position:
t = pya.Trans.from_s('r0 %s, %s' % (x+20000,y))
instY1 = cell.insert(pya.CellInstArray(cell_ebeam_y.cell_index(), t))

# Version 2: attach it to an existing component, then move relative
instY2 = connect_cell(instGC2, 'opt1', cell_ebeam_y, 'opt1')
instY2.transform(Trans(20000,-10000))

# Waveguides:

connect_pins_with_waveguide(instGC1, 'opt1', instY1, 'opt1', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instGC2, 'opt1', instY2, 'opt1', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instY1, 'opt2', instY2, 'opt3', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instY1, 'opt3', instY2, 'opt2', waveguide_type=waveguide_type,turtle_B=[25,-90])

# 2nd MZI using Dream Photonics 1x2 splitter
# grating couplers, place at absolute positions
x,y = 150000, 15000
t = pya.Trans.from_s('r0 %s,%s' % (x,y))
instGC1 = cell.insert(pya.CellInstArray(cell_ebeam_gc.cell_index(), t))
t = pya.Trans.from_s('r0 %s,%s' % (x,y+127000))
instGC2 = cell.insert(pya.CellInstArray(cell_ebeam_gc.cell_index(), t))

# automated test label
text = pya.Text ("opt_in_TE_1550_device_MZI_Dream", t)
cell.shapes(ly.layer(TECHNOLOGY['Text'])).insert(text).text_size = 5/dbu

# Y branches:
# Version 1: place it at an absolute position:
t = pya.Trans.from_s('r0 %s, %s' % (x+20000,y))
instY1 = cell.insert(pya.CellInstArray(cell_ebeam_y_dream.cell_index(), t))

# Version 2: attach it to an existing component, then move relative
instY2 = connect_cell(instGC2, 'opt1', cell_ebeam_y_dream, 'opt1')
instY2.transform(Trans(20000,-10000))

# Waveguides:

connect_pins_with_waveguide(instGC1, 'opt1', instY1, 'opt1', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instGC2, 'opt1', instY2, 'opt1', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instY1, 'opt2', instY2, 'opt3', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instY1, 'opt3', instY2, 'opt2', waveguide_type=waveguide_type,turtle_B=[25,-90])



# Zoom out
lv.clear_object_selection()
lv.zoom_fit()
lv.max_hier()

# Save the layout, without PCell info, for fabrication
save_options = pya.SaveLayoutOptions()
save_options.write_context_info=False  # remove $$$CONTEXT_INFO$$$
save_options.format='GDS' # standard format
save_options.format='OASIS' # smaller file size
save_options.oasis_compression_level=10
file_out = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../EBeam_LukasChrostowski_MZI.%s" % save_options.format[0:3])
print("saving output %s: %s" % (save_options.format, file_out) )
ly.write(file_out,save_options)
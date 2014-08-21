from collections import  defaultdict
import prettytable
import ctadpole

cell_types = {1: 'RB', 2: 'dlc', 3: 'aIN', 4: 'cIN', 5: 'dIN', 6: 'MN', 7: 'dla'}
cells = ctadpole.load_cells('CellList-EvenFull.txt', 'Connectome-EvenFull.txt')
n_cells = len(cells)


cell_pops = defaultdict(list)
for index, cell in enumerate(cells):
    is_lhs = index < n_cells/2
    key =  (is_lhs, cell_types[cell.type_id+1])
    cell_pops[ key ].append(cell)


# Quick-check the ID's tie up:
for (is_lhs,cell_type), cell_list in cell_pops.items():
    for index, cell in enumerate(cell_list):
        if is_lhs:
            assert cell.relative_id == index
        else:
            assert cell.relative_id == index + len(cell_list)

        # Set the target ID to be 'per population per side', not just 'per population'
        cell.relative_id = index






# Map cell-> population:
cell_to_popkey ={ cell:popkey for popkey, cell_list in cell_pops.items() for cell in cell_list }


# Map population -> size
pop_sizes = {popkey: len(cell_pop) for (popkey, cell_pop) in cell_pops.items()}


# Create a dictionary of '(popkey),(popkey)' -> [(src_index,tgt_index),(src_index,tgt_index)]
projections = defaultdict( set)
# OK, so now lets sort out the connection matrices between the different populations:
for (is_lhs,cell_type), cell_list in cell_pops.items():
    for index,tgt_cell in enumerate(cell_list):
        for src_cell  in tgt_cell.incoming_connections:
            src_pop = cell_to_popkey[src_cell]
            tgt_pop = cell_to_popkey[tgt_cell]

            src_index = src_cell.relative_id
            tgt_index = tgt_cell.relative_id

            projections[(src_pop, tgt_pop)].add( (src_index, tgt_index))


# Extract the position of each cell:
cell_positions = defaultdict( dict)
for cell, popkey in cell_to_popkey.items():
    cell_positions[popkey][cell.relative_id] = cell.pos


# Make into a dictionary = popkey -> [x0,x1,x2,x3..]
population_positions = {}
for pop,values in cell_positions.items():
    ind_pos = [ (cell_index, pos) for (cell_index, pos) in sorted(values.items()) ]
    inds = [ x[0] for x in ind_pos]
    positions =  [ x[1] for x in ind_pos]
    assert inds == list(range(len(inds)))
    population_positions[pop] = positions




def print_pop_info(pops, pop_sizes, projections):
    # Populations:
    tbl = prettytable.PrettyTable( ['Population', 'Count'])
    for pop in pops:
        tbl.add_row( [str(pop), pop_sizes[pop] ])
    print 'Population sizes:'
    print '-----------------'
    print tbl
    print '\n'


    # Synapses:
    tbl = prettytable.PrettyTable( [''] + [str(p) for p in pops])
    for src_pop in pops:
        tbl.add_row( [str(src_pop)] + [ len(projections[(src_pop, tgt_pop)]) for tgt_pop in pops])
    print 'Synaptic Projections:'
    print '---------------------'
    print 'Top->Bottom => src-populations'
    print 'Left->Right => dst-populations'
    print tbl






#SynapticProjectionType = namedtuple('SynapticProjectionType', ['type', 'gbar'])

def merge_populations(pop_sizes, projections, pop_merge_details, projection_merge_details, population_positions):

    # Sanity check, make sure that we are merging the same populations:
    # TODO:

    # Calculate the offsets of each old population in the new population:
    old_population_locations = {}
    new_popsizes = {}
    for new_pop_name, included_pops in sorted(pop_merge_details.items()):
        print 'New Population:', new_pop_name
        new_pop_size = 0
        for incl_pop in included_pops:
            old_population_locations[incl_pop] = (new_pop_name, new_pop_size, pop_sizes[incl_pop] )
            new_pop_size += pop_sizes[incl_pop]
        new_popsizes[new_pop_name] = new_pop_size


    # Build the projection-merge-details into something a bit neater:
    projection_types = defaultdict( list)
    for projection_detail in projection_merge_details:
        src,tgt = projection_detail['between'].split("->")
        projection_types[ (src, tgt) ].append( (projection_detail['syn_type'], projection_detail['g']))

    new_projections = defaultdict( list)
    # OK, now remap each of the existing projections:
    for (src_pop, tgt_pop), indices in projections.items():
        if not indices:
            continue
        src_pop_new, src_index_offset, src_pop_size = old_population_locations[src_pop]
        tgt_pop_new, tgt_index_offset, tgt_pop_size = old_population_locations[tgt_pop]


        #print (src_pop[1], tgt_pop[1])
        pop_to_pop_projections = projection_types[ (src_pop[1], tgt_pop[1])]
        assert pop_to_pop_projections

        for proj in pop_to_pop_projections:
            new_key = (src_pop_new, tgt_pop_new, proj)
            for (i,j) in indices:
                new_projections[new_key].append( (i+src_index_offset, j+tgt_index_offset))

    # And remap the positions:
    new_population_positions = dict()
    for new_pop_name, included_pops in sorted(pop_merge_details.items()):
        new_population_positions[new_pop_name] = []
        for incl_pop in included_pops:
            new_population_positions[new_pop_name].extend( population_positions[incl_pop])



    return new_popsizes, new_projections, old_population_locations, new_population_positions






pops = sorted(cell_pops.keys())
print_pop_info(pops, pop_sizes, projections)













# Merge
pop_merge_details = {
    'NondINs' : sorted( [(False,'RB'), (False,'dlc'),(False,'aIN'), (False,'cIN'), (False, 'MN'), (False,'dla'), (True,'RB'), (True,'dlc'),(True,'aIN'), (True,'cIN'), (True, 'MN'), (True,'dla') ] ),
    'dINs' : sorted( [(False,'dIN'), (True,'dIN')] )
}
projection_merge_details = [

 { "between": "RB->dlc",	 "syn_type": "ampa",	"g":  8.0, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "RB->dla",	 "syn_type": "ampa",	"g":  8.0, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dlc->dIN",	 "syn_type"	: "nmda",	"g"	: 1.0, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dla->dIN",	 "syn_type"	: "nmda", 	"g"	: 0.29, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dIN->dIN",	 "syn_type"	: "nmda", 	"g"	: 0.15, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dIN->dIN",	 "syn_type"	: "ampa", 	"g"	: 0.593, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dIN->cIN",	 "syn_type"	: "ampa", 	"g"	: 0.593, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "cIN->dIN",	 "syn_type"	: "inh", 	"g"	: 0.435, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "cIN->cIN",	 "syn_type"	: "inh",	"g"	: 0.435, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "RB->dIN",	 "syn_type"	: "ampa",	"g":  0.593, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dlc->dlc",	 "syn_type"	: "nmda",	"g":  0.29, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dlc->aIN",	 "syn_type"	: "nmda", 	"g"	: 0.29, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dlc->cIN",	 "syn_type"	: "nmda",	"g":  0.29, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dlc->MN",	 "syn_type"	: "nmda", 	"g"	: 0.29, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "aIN->dlc",	 "syn_type"	: "inh", 	"g"	: 0.435, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "aIN->aIN",	 "syn_type"	: "inh", 	"g"	: 0.435, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "aIN->cIN",	 "syn_type"	: "inh", 	"g"	: 0.435, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "aIN->dIN",	 "syn_type"	: "inh", 	"g"	: 0.435, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "aIN->MN",	 "syn_type"	: "inh", 	"g"	: 0.435, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "aIN->dla",	 "syn_type"	: "inh", 	"g"	: 0.435, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "cIN->dlc",	 "syn_type"	: "inh",	"g"	: 0.435, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "cIN->aIN",	 "syn_type"	: "inh", 	"g"	: 0.435, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "cIN->MN",	 "syn_type"	: "inh", 	"g"	: 0.435, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dIN->dlc",	 "syn_type"	: "ampa", 	"g"	: 0.593, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dIN->aIN",	 "syn_type"	: "ampa", 	"g"	: 0.1, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dIN->MN",	 "syn_type"	: "ampa", 	"g"	: 0.593, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dIN->dla",	 "syn_type"	: "ampa", 	"g"	: 0.593, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dla->dlc",	 "syn_type"	: "nmda", 	"g"	: 0.29, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dla->aIN",	 "syn_type"	: "nmda", 	"g"	: 0.29, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dla->cIN",	 "syn_type"	: "nmda", 	"g"	: 0.29, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dla->MN",	 "syn_type"	: "nmda", 	"g"	: 0.29, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "dla->dla",	 "syn_type"	: "nmda", 	"g"	: 0.29, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "MN->aIN",	 "syn_type"	: "ampa", 	"g"	: 0.593, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "MN->cIN",	 "syn_type"	: "ampa", 	"g"	: 0.593, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "MN->dIN",	 "syn_type"	: "ampa", 	"g"	: 0.593, "fixed_delay": 1.0, "dist_delay":  0.0035 },
 { "between": "MN->MN",	 "syn_type"	: "ampa", 	"g"	: 0.593, "fixed_delay": 1.0, "dist_delay":  0.0035 }
]




#Merge the populations
new_popsizes, new_projections, old_population_locations, new_population_positions = merge_populations(pop_sizes, projections, pop_merge_details, projection_merge_details, population_positions)



print 'Reduced Populations:'
tbl = prettytable.PrettyTable( ['Old Population', 'New location'])
for old_pop, (new_pop, offset,size) in sorted(old_population_locations.items()):
    tbl.add_row( [old_pop,  str( (new_pop, offset,size))])
print tbl



tbl = prettytable.PrettyTable( ['Population', 'Count'])
for k,v in  sorted(new_popsizes.items()):
    tbl.add_row([k, v])
print tbl


tbl = prettytable.PrettyTable( ['Synapse-Type', 'Count'])
for k,v in  sorted(new_projections.items()):
    tbl.add_row([k, len(v)])

print tbl




print new_population_positions



import cPickle as pickle
op_filename = 'mh_reduced_connectome.pickle'
print 'Writing to pickle file:', op_filename
with open(op_filename, 'w') as f:
    pickle.dump([new_popsizes, new_projections, old_population_locations, new_population_positions], f)


# -*- coding: utf-8 -*-
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
# FreeSolv from MoleculeNet for the prediction of hydration free
# energy of small molecules in water

import pandas as pd

from dgl.data.utils import get_download_dir, download, _get_dgl_url, extract_archive

from .csv_dataset import MoleculeCSVDataset

__all__ = ['CycPep']

class CycPep(MoleculeCSVDataset):
    r"""CycPep from MoleculeNet for the prediction of membrane permability


    Parameters
    ----------
    smiles_to_graph: callable, str -> DGLGraph
        A function turning a SMILES string into a DGLGraph. If None, it uses
        :func:`dgllife.utils.SMILESToBigraph` by default.
    node_featurizer : callable, rdkit.Chem.rdchem.Mol -> dict
        Featurization for nodes like atoms in a molecule, which can be used to update
        ndata for a DGLGraph. Default to None.
    edge_featurizer : callable, rdkit.Chem.rdchem.Mol -> dict
        Featurization for edges like bonds in a molecule, which can be used to update
        edata for a DGLGraph. Default to None.
    load : bool
        Whether to load the previously pre-processed dataset or pre-process from scratch.
        ``load`` should be False when we want to try different graph construction and
        featurization methods and need to preprocess from scratch. Default to False.
    log_every : bool
        Print a message every time ``log_every`` molecules are processed. Default to 1000.
    cache_file_path : str
        Path to the cached DGLGraphs, default to 'freesolv_dglgraph.bin'.
    n_jobs : int
        The maximum number of concurrently running jobs for graph construction and featurization,
        using joblib backend. Default to 1.

    Examples
    --------

    >>> from dgllife.data import FreeSolv
    >>> from dgllife.utils import SMILESToBigraph, CanonicalAtomFeaturizer

    >>> smiles_to_g = SMILESToBigraph(node_featurizer=CanonicalAtomFeaturizer())
    >>> dataset = FreeSolv(smiles_to_g)
    >>> # Get size of the dataset
    >>> len(dataset)
    642
    >>> # Get the 0th datapoint, consisting of SMILES, DGLGraph and hydration free energy
    >>> dataset[0]
    ('CN(C)C(=O)c1ccc(cc1)OC',
     DGLGraph(num_nodes=13, num_edges=26,
              ndata_schemes={'h': Scheme(shape=(74,), dtype=torch.float32)}
              edata_schemes={}),
     tensor([-11.0100]))

    We also provide information for the iupac name and calculated hydration free energy
    of the compound.

    >>> # Access the information mentioned above for the ith datapoint
    >>> dataset.iupac_names[i]
    >>> dataset.calc_energy[i]

    We can also get all these information along with SMILES, DGLGraph and hydration free
    energy at once.

    >>> dataset.load_full = True
    >>> dataset[0]
    ('CN(C)C(=O)c1ccc(cc1)OC',
     DGLGraph(num_nodes=13, num_edges=26,
              ndata_schemes={'h': Scheme(shape=(74,), dtype=torch.float32)}
              edata_schemes={}), tensor([-11.0100]),
     '4-methoxy-N,N-dimethyl-benzamide',
     -9.625)
    """
    def __init__(self,
                 smiles_to_graph=None,
                 node_featurizer=None,
                 edge_featurizer=None,
                 load=False,
                 log_every=1000,
                 cache_file_path='./cycpep_dglgraph.bin',
                 n_jobs=1):

        self._url = '/mnt/c/Users/schau/Documents/PerpetualMedicine/data/all_cycpep_data.csv'
        dir_path = '/mnt/c/Users/schau/Documents/PerpetualMedicine/data'
        df = pd.read_csv(dir_path + '/all_cycpep_data.csv')

        super(CycPep, self).__init__(df=df,
                                       smiles_to_graph=smiles_to_graph,
                                       node_featurizer=node_featurizer,
                                       edge_featurizer=edge_featurizer,
                                       smiles_column='SMILES',
                                       cache_file_path=cache_file_path,
                                       task_names=['Permeability'],
                                       load=load,
                                       log_every=log_every,
                                       init_mask=False,
                                       n_jobs=n_jobs)

        self.load_full = False

        # Papers
        self.paper = df['Source'].tolist()
        self.paper = [self.paper[i] for i in self.valid_ids]
        # Chemistry cluster
        self.chem_cluster = df['cluster'].tolist()
        self.chem_cluster = [self.chem_cluster[i] for i in self.valid_ids]

        # Id from CycPeptMPDB
        self.cycpep_id = df['CycPeptMPDB_ID'].tolist()
        self.cycpep_id = [self.cycpep_id[i] for i in self.valid_ids]

    def __getitem__(self, item):
        """Get datapoint with index

        Parameters
        ----------
        item : int
            Datapoint index

        Returns
        -------
        str
            SMILES for the ith datapoint
        DGLGraph
            DGLGraph for the ith datapoint
        Tensor of dtype float32 and shape (1)
            Labels of the ith datapoint
        str, optional
            IUPAC nomenclature for the ith datapoint, returned only when
            ``self.load_full`` is True.
        float, optional
            Calculated hydration free energy for the ith datapoint, returned only when
            ``self.load_full`` is True.
        """
        if self.load_full:
            return self.smiles[item], self.graphs[item], self.labels[item], \
                   self.paper[item], self.chem_cluster[item], self.cycpep_id[item]
        else:
            return self.smiles[item], self.graphs[item], self.labels[item]

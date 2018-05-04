# k-shortest-path
[![Build Status](https://travis-ci.com/datagovsg/k-shortest-path.svg?token=QdYT7V5eiyXqAzGySBss&branch=dev)](https://travis-ci.com/datagovsg/k-shortest-path)
[![Python version](https://img.shields.io/badge/python-2.7-blue.svg)](https://shields.io/)
[![Python version](https://img.shields.io/badge/python-3.6-blue.svg)](https://shields.io/)

k-shortest-path implements various algorithms for the K shortest path problem. Currently, the only implementation is for the deviation path algorithm by Martins, Pascoals and Santos (see [1](https://www.mat.uc.pt/~eqvm/cientificos/investigacao/Artigos/deviation.ps.gz) and [2](http://www.dis.uniroma1.it/challenge9/papers/santos.pdf)) to generate all simple paths from from (any) source to a fixed target.

## Installation
```bash
pip3 install pipenv
git clone git@github.com:datagovsg/k-shortest-path.git
cd k-shortest-path
pipenv install
```

## Usage
Create one **kspath.deviation_path.mps.SingleTargetDeviationPathAlgorithm** object for all `source-target` pairs with a fixed `target` as this will reduce the number of calls to Dijkstra's algorithm
### 1. **kspath.deviation_path.mps.SingleTargetDeviationPathAlgorithm**.create_from_graph(_G_, _target_, _weight_, _max_consecutive_cycles_=500)

**Parameters**
* _G_ (NetworkX graph)
* _target_ (node) – Ending node for path
* _weight_ (string) – Name of the edge attribute to be used as a weight. If None all edges are considered to have unit weight.
* _max_consecutive_cycles_ (int) – Maximum number of deviation paths to search before switching to Yen's algorithm

**Returns**
* _kspath.deviation_path.mps.SingleTargetDeviationPathAlgorithm_ object

**Raises**
* _NodeNotFound_ – If target does not exist in _G_

### 2. **kspath.deviation_path.mps.SingleTargetDeviationPathAlgorithm**.shortest_simple_paths(_source_)

**Parameters**
* _source_ (node) – Starting node for path

**Returns**
* _generator_

**Raises**
* _NodeNotFound_ – If source does not exist in _G_

```python
from kspath.deviation_path.mps import SingleTargetDeviationPathAlgorithm

dpa_mps = SingleTargetDeviationPathAlgorithm.create_from_graph(G=G, target=6, weight='weight')
paths = []
for path_count, path in enumerate(dpa_mps.shortest_simple_paths(source=1), 1):
    paths.append(path)
    if path_count == 100:
        break
```

## Tests
For simple test cases, install pytest and run in the top level directory.
```bash
pipenv install pytest --dev
pytest -m fast
```

For a larger test, run
```
pytest -m slow
```
This takes a couple of minutes to complete.

For more comprehensive test cases, run
```bash
pytest -m comprehensive
```
This takes approximately fifteen days to complete. 

*Both **slow** and **comprehensive** tests requires the right credentials to download the data from a private repo.

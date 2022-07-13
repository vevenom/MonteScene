# MonteScene

MonteScene is a python module that simplifies implementation of efficient search algorithms based on Monte Carlo Tree 
Search (MCTS), with optional simultaneous refinement, for applications in scene understanding. Through this module, we 
want to motivate and inspire developers and researchers to apply and further extend MonteScene for their own
 original applications. 
 
_Note_: We are working on releasing documentation and toy examples in next few months. For now, you can use the issue system if you have more specific questions about using MonteScene for your own scene understanding tasks. 

## News 

* [13.7.2022] The first toy example, PolygonGame, is now released.

* [06.07.2022] MonteScene is public.

## TODO

* [Coming Soon] PolygonGame implementation 

* [In Progress] PolygonRefinementGame implementation

* [In Progress] 3DPrimitivesGame implementation

## Introduction

Historically, MCTS was commonly researched as an efficient search algorithm for playing games of high state-complexity 
such as Chess, Go, and Shogi. As we draw inspiration from these successes, we define a _Proposals Selection Game_  as a 
family of problems in scene understanding for which our approach is applicable. 

_Proposals selection game_ is a very simple and a very general single-player game. We initialize our game by generating 
a large set of proposals and the goal of the game is to retrieve a subset which best describes the input scene, based on
a defined scoring function. Then, a move in the game consists of selecting one proposal from the pool. As the rule of 
scene understanding dictates that some proposals are mutually incompatible, every time we pop one proposal from the pool, 
we remove all incompatible proposals from the pool as well. The game continues until the pool of proposals becomes empty, 
after which the game ends and the final score is calculated representing the fitness of the selected solution to the given 
scene. 

Our MonteScene implementation is used to efficiently find the optimal solution by replaying proposals selection game 
by balancing exploitation and exploration. For some games proposal generation is not perfect, and the initial proposals might
be noisy. This framework also supports joint selection and refinement of noisy proposals.


## Projects Powered by MonteScene

### MCSS -- Monte Carlo Scene Search for 3D Scene Understanding

<img src="https://github.com/vevenom/MonteScene/blob/main/example_images/mcss.gif?raw=true">

MonteScene is applied for 3D reconstruction of scene components, including structrural elements and CAD-models for furniture elements.

[Video](https://www.youtube.com/watch?v=F6vPmQ-TQ2s) |
[Paper](https://openaccess.thecvf.com/content/CVPR2021/html/Hampali_Monte_Carlo_Scene_Search_for_3D_Scene_Understanding_CVPR_2021_paper.html) | [Project Page](https://www.tugraz.at/institute/icg/research/team-lepetit/research-projects/monte-carlo-scene-search-for-3d-scene-understanding/) 

### MonteFloor -- Extending MCTS for Reconstructing Accurate Large-Scale Floor Plans

<img src="https://www.tugraz.at/fileadmin/user_upload/Institute/ICG/Images/team_lepetit/stekovic/MonteFloor/floorsp_12.gif?raw=true" width="200px">

MonteScene with refinement is applied for floor plan reconstruction task, using our framework for jointly selecting and refining polygonal proposals.

[Video](https://www.youtube.com/watch?v=RJi4v5nQnfE&feature=emb_title) |
[Paper](https://openaccess.thecvf.com/content/ICCV2021/html/Stekovic_MonteFloor_Extending_MCTS_for_Reconstructing_Accurate_Large-Scale_Floor_Plans_ICCV_2021_paper.html) | [Project Page](https://www.tugraz.at/institute/icg/research/team-lepetit/research-projects/montefloor-extending-mcts-for-reconstructing-accurate-large-scale-floor-plans/)

### MonteRoom -- MCTS with Refinement for Proposals Selection Games in Scene Understanding

<img src="https://github.com/vevenom/MonteScene/blob/main/example_images/monteroom.gif?raw=true?raw=true" width="200px">


MonteScene with refinement is applied for 3D room layout estimation from single images, using our framework for jointly selecting and refining 3d planar  polygonal proposals.

[Paper](https://arxiv.org/abs/2207.03204)

## Toy Examples

### PolygonGame

<img src="https://github.com/vevenom/MonteScene/blob/main/example_images/polygongame.gif?raw=true" width="200px">

MonteScene is applied for selecting 2d polygon proposals that best fit an input image. Bachelor project authored by: [nik-por](https://github.com/nik-por)

[Code](https://github.com/nik-por/MonteScene.Examples.Polygon)
## Key Features

* Simple-to-use and flexible framework for integrating MonteScene (optionally with _refinement_) for any 
scene understanding problem that can be casted as a proposals selection game. 

* Framework integrates base classes ``Proposal``, ``Game``, and ``MCTSLogger`` with basic functionalities
that are common in all proposals selection games. Through class inheritance, it is easy to adapt base classes to a 
specific task by implementing task-specific functionalities (such as proposals generation, 
score calculation and visualizations). That is it! By modfying ``run.py`` script, developers can  quickly run MonteScene by 
following provided instructions in the script. 

* Flexible settings that enable/disable certain features.

* In Progress: Toy examples demonstrating how to use MonteScene for different applications in scene understanding.

## Setup

1. Acitvate your virtual environment;
2. Clone this repository;
3. You can install MonteScene as a package by running ``` pip install . ``` from the root directory of this repository and installing the required dependencies.

## Citation

MonteScene is a result of our findings from several publications. Hence, if you use MonteScene in your 
research project, please consider citing following papers:

* ["Monte Carlo Scene Search for 3D Scene Understanding"](https://arxiv.org/abs/2103.07969) first generates a large set 
of proposals by fitting CAD models of furniture and structural elements to the input scene. Then, MonteScene is used to 
find the optimal subset which best describe the input scene.

```bibtex
@inproceedings{hampali2021monte,
  title={Monte carlo scene search for 3d scene understanding},  
  author={Hampali, Shreyas and Stekovic, Sinisa and Sarkar, Sayan Deb and Kumar, Chetan S and Fraundorfer, Friedrich and Lepetit, Vincent},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},  
  year={2021}
}
```

*  ["MonteFloor: Extending MCTS for Reconstructing Accurate Large-Scale Floor Plans"](https://arxiv.org/abs/2103.11161) 
introduces the refinement step. Hence, MonteScene jointly selects and refines proposals to improve the fitness with 
respect to the input scene. 

```bibtex
@inproceedings{stekovic2021montefloor,
  title={Montefloor: Extending mcts for reconstructing accurate large-scale floor plans},  
  author={Stekovic, Sinisa and Rad, Mahdi and Fraundorfer, Friedrich and Lepetit, Vincent},  
  booktitle={Proceedings of the IEEE/CVF International Conference on Computer Vision},  
  year={2021}
}
```

* ["MCTS with Refinement for Proposals Selection Games in Scene Understanding"](https://arxiv.org/abs/2207.03204) is an extension showing that our MCTS
with refinement scheme can be generalized to different problems in Scene Understanding.

```bibtex
@misc{
  author = {Stekovic, Sinisa and Rad, Mahdi and Moradi, Alireza and Fraundorfer, Friedrich and Lepetit, Vincent},
  keywords = {Computer Vision and Pattern Recognition (cs.CV), Artificial Intelligence (cs.AI), Computer Science and Game Theory (cs.GT), FOS: Computer and information sciences, FOS: Computer and information sciences},
  title = {MCTS with Refinement for Proposals Selection Games in Scene Understanding},
  publisher = {arXiv},
  year = {2022}
  }
```

## Contributors in Alphabetical Order

 * Shreyas Hampali, Chetan S. Kumar, Alireza Moradi, Mahdi Rad, Sayan Deb Sarkar, Sinisa Stekovic
 
 * Research Supervisors: Friedrich Fraundorfer and Vincent Lepetit


## License
This work is distributed under BSD Clear license. See LICENSE file.

## Acknowledgment 

This work was supported by the Christian Doppler Laboratory for Semantic 3D Computer Vision, funded in part by Qualcomm Inc.

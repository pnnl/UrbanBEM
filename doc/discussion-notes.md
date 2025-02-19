# Discussions notes

organized in chronological order

- [Discussions notes](#discussions-notes)
  - [Meeting minutes for discussion on 01/14/2020](#meeting-minutes-for-discussion-on-01142020)
    - [About "Lego" modeling approach](#about-lego-modeling-approach)
    - [Do we want to have pre-simulated load profiles to answer questions](#do-we-want-to-have-pre-simulated-load-profiles-to-answer-questions)
    - [Benefits of the proposed modeling approach](#benefits-of-the-proposed-modeling-approach)
    - [Potential issues (not in the FY20 scope)](#potential-issues-not-in-the-fy20-scope)
    - [Zoning heuristics](#zoning-heuristics)
    - [More](#more)
  - [Additional information from discussion between Jian and Jerry on 01/22/2020](#additional-information-from-discussion-between-jian-and-jerry-on-01222020)
  - [Meeting minutes from meeting w/ Jian, Jeremy, Yunyang, Jerry on 01/30/2020](#meeting-minutes-from-meeting-w-jian-jeremy-yunyang-jerry-on-01302020)
    - [BEM modeling strategy](#bem-modeling-strategy)
  - [2nd meeting minutes on 01/30/2020](#2nd-meeting-minutes-on-01302020)
  - [Modularized modeling process diagram](#modularized-modeling-process-diagram)
  - [March Action Items Planning](#march-action-items-planning)
    - [March hour spending by the end of March](#march-hour-spending-by-the-end-of-march)
    - [Action items derived from planning slides](#action-items-derived-from-planning-slides)
      - [Model generation development](#model-generation-development)
      - [Actions for other matters](#actions-for-other-matters)
  - [Decisions on 03/03/2020](#decisions-on-03032020)
  - [Discussions on 03/04/2020](#discussions-on-03042020)

## Meeting minutes for discussion on 01/14/2020

### About "Lego" modeling approach

- We had two different "Lego" modeling approach on the table
  1. Simplify and disassemble a building model into multiple bricks according to thermal zones and for each brick, creating a separate model (idf) and run simulation against
  2. Simplify and disassemble a building model into multiple bricks according to thermal zones, but all bricks are still inside one model (idf) and will be simulated together
     We lean towards the second approach
- If everything is a single zone system, then either of the above two approaches works. If it is a multi-zone system, then approach 1 won't work. Within the same idf, we can assign multiple zones in the same HVAC system.

### Do we want to have pre-simulated load profiles to answer questions

- This depends on the application. Most use cases would require us to run simulations and that the main capability we target.

### Benefits of the proposed modeling approach

- Comparing with ground up case-specific modelling (i.e. modeling in our prototypes), in this project, we do on the fly zoning and would have more flexibility. Easier to troubleshooting, and do benchmarking
- Comparing with existing simulation-based benchmarking tool. Our lego modeling approach is more sophisticated and is expected to yield more accurate results. In FY20, we'll not have have much effort to do benchmarking. We can do two things: 1) to compare the shape and order of magnitude of aggregated load curve with some existing ones; 2) to compare our results from logo-based prototype models with those from a corrsponding EPSTD prototype models.
  - This needs to be confirmed.
  - Comparing with Comcheck?
  - Some earlier benchmarking tool would build a simple rectangle space model to simulate the baseline energy usage.

### Potential issues (not in the FY20 scope)

- Inter-building shading: LBNL's Tianhen Hong developed an EP feature to capture the inter-bldg shading impact. More detailed information is not acquired yet.
- Inter-building airflow impact: Unknown knowledge

### Zoning heuristics

- Rules in the ASHRAE appendix C is probably a better resource than digging the Comcheck source code.
- Jerry will have a look at the appendix and Jian will lead Jerry on it later.

### More

- Yunyang did a review on existing large scale modeling approaches, this is potentially very helpful and we shall later have him involved in the project. (Jian will decide when to include him)
- Since several third-party software, e.g. Eppy/Geomeppy, Modelkit, openstudio, has templates or routines to automatically inject HVAC systems in to the model. We shall aim at developing a set of interfaces to talk to these tools when building our models. This can also be a selling point especially since we are building and showcasing a framework

## Additional information from discussion between Jian and Jerry on 01/22/2020

- We are going to divide the model generation step into the following separate steps and tackle each with different focuses
  1. geometry
     - this requires heavy development work. The general idea is to follow the ASHRAE 90.1 App C. The target is to have a simplified and modular way to create geometry and zoning following the idea of App C. The end results will not be as detailed as What's been done in COMCheck. We need to show the lego idea without considering sophisticated systems and scenarios / corner cases.
     - Rewrite COMCheck code into Python code leveraging eppy is too much work for this project. We will just use App C and simplify details while keeping the conceptual ideas.
     - This would not be a selling point of the project
  2. load
     - We will leverage existing methods in COMCheck and Asset Score projects to generate loads.
  3. schedule
     - We will leverage the method being developed in the OCC sensor project to generate the schedules.
  4. HVAC systems
     - More discussion is needed to substantiate this part
     - In this part, we will try to develop a framework selling point of having different interfaces utilizing existing HVAC system templates from
       - Eppy
       - Modelkit
     - We need to double check the appropriateness of interfacing with Eppy / Modelkit templates. It should be fine though.
- We are still in the stage of planning, but we are getting things clearer. We may need to organize a meeting with everybody (Jian, Jeremy, Yunyang, Jerry, Yan, Amanda) and collect feedback and thoughts to finalize and detail the plan, and discuss the potential use case / analysis of the large scale simulation results.

## Meeting minutes from meeting w/ Jian, Jeremy, Yunyang, Jerry on 01/30/2020

Texts in `[]` are Jerry's comments while taking the notes.

- gap to fill: evaluate impacts at large scale of buildings instead of individual buildings
- selling point of nrel comstock: use the original prototypes and scale them to simpler stretched geometry etc.
- no typical method to analyze the results in existing studies.
- PNNL internal reviews emphasizes the gap of limited stock data and from different sources / formats. This is not what we want. We don't want to provide data to other people, we want to create end-to-end framework to analyze the results. We want to replace others' method and provide better solution
- [we will need to have interfaces if we want to collaborate with other people, to use their existing implementations. So it is probably essential to have a detailed and standarlized process ot doing end-to-end urban-sim]

* possible data source: comcheck, rescheck (not a core of our work)
* Andrew Parker's presentation about comstock: collect data from different sources, e.g. census, in different formats

### BEM modeling strategy

- the overall plan is to convert building characteristics to BEMs
- the big assumption is: we won't be able to generate the exact shape of the building. We capture the total conditioned area of the bldg and the total exterior area of different surfaces
- another assumption: we believe the interactions between different thermal zones are negligible.
- we will create thermal zones that host the external envelope and host the floor areas as the user inputs, but the shape won't be accurate
- how to model multi-zone vav system having separate zones being tagged. This is not the current focus.
- why cannot we use comcheck to generate BEM: expandability of our way of doing the model. We can treat as if Comcheck does not exist and claim what we do in this project (the LEGO zoning etc) as the contribution.
- Yunyang: review of existing urban-scale simulation. Some do not fall in the focuses of our work, we may not need to have a review of the work, and we may not have the resources to do so. Jian has the frontiers of this area in mind and will discuss in our next meeting. I.e. Jian will talk about the existing tools doing urban-sim when we can meet together again.
- We will hold the implementation work until we figure out the detailed things we are going to do that are different from existing studies.

## 2nd meeting minutes on 01/30/2020

our calibration at bottom levels make it reasonable to study vibrations and interactions

others research, higher resolution means higher variances.

our calibration can calibrate time series

others calibration accumulative data.

## Modularized modeling process diagram

![urbansim-flow](img/URBANSIM-FLOW.jpg)

## March Action Items Planning

### March hour spending by the end of March

- Jian: 30hr
- Jeremy: 40hr
- Yunyang: 100hr
- Jerry: 100hr

### Action items derived from planning slides

#### Model generation development

_Assign following items to people_

| Action item (**Bold for immediate tasks**)                                                         | Outcome                                    | Assignee (tentative) | Task Schedule                    | Notes                                              |
| -------------------------------------------------------------------------------------------------- | ------------------------------------------ | -------------------- | -------------------------------- | -------------------------------------------------- |
| **1. Pick a specific bldg character vector and create idf objects generated after each processor** | several idfs                               | Yunyang              | Start with geometry idf by Mar 3 | we will discuss once Yunyang created the idf files |
| **2. Detail modeling strategy for Geometry Processor**                                             | narrative document / code with explanation | Jian, Jerry          | Start once geometry idf in place | deriving geometry info from cbecs raw data         |
| **3. Detail modeling strategy for Load Processor**                                                 | narrative document / code with explanation | Jeremy, Jerry        | After the above task             |
| 4. Detail modeling strategy for Schedule Processor                                                 | narrative document / code with explanation | Yunyang, Jerry       | After the HVAC processor (5)     |
| 5. Detail modeling strategy for HVAC Processor                                                     | narrative document / code with explanation | Jeremy, Yunyang      | Start once hvac idf inplace      |
| 6. Code detailed modeling strategies                                                               | working implementation                     | Yunyang, Jerry       | After all above                  |

#### Actions for other matters

- functional coding style. Jeremy is in charge.
- Discuss the following next question
  - post processing artifacts specification. Jeremy, Yunyang, Jerry
  - Framework infrastructure. Jerry.
    - Need to decide on whether using PIC or AWS once we have more details about what tasks we are dealing with wrt Post-processing data file size / number / operations.

## Decisions on 03/03/2020

The following on based on calls of Jian <-> Jerry and Jeremy <-> Jerry,

- We are going to give up setting up the example idf files outputed after each processor.
- To enable the simultaneous development of several processors, we will need to settle a naming convention of objects and paramters.
  - Geomeppy seems to not have a consistent naming convention among all of its automatically generated contents. However, for the most part, it uses `Title Case` for naming zones and surfaces. We are going to use this for now and we are going to learn about geomeppy's naming convention from its source code
  - The coordination of naming convention between different processor implementations should not be very difficult during development
- Jerry's going to put his naming conventions of the geometry modeling in a separate file in this folder.
- We may write some helper code around Geomeppy / eppy, and their owners should be happy to have those. On the other hand, we can fork them, or have code maintained in our own repo.
- Under the general design of the system, certain things written in the current geometry.py are suppose to be in other places. For example, alternate constructors are essentially dataset wrappers. The current implementation is for easy development and testing. We can organize this later.

Bullets in Jian's email:

> 1. Let’s use Eppy’s method to generate geometry because it is quick and meet our needs. We’ll customize and refine the models when necessary.
> 2. Let’s change our previous strategy: use IDF example to guide the Processor development. Instead, we can use what’s available from Eppy as much as possible. So, this means we’ll not use the geometry file generated by Yunyang. It might be useful for us later.
> 3. Jeremy knows both Eppy and existing EPSTD and OSSTD data and naming conventions. He will provide some guideline about naming conventions and tell us when we can use existing data from EPSTD and OSSTD.
> 4. Jerry has some preference about the programming style convention and will provide some suggestions.

## Discussions on 03/04/2020

Following the revised action items, Jeremy, Yunyang and Jerry had a discussion to figure out the immedeiate code development plan as follows

1. The geometry output idf example is already generated by the implementated geometry rule. Jerry is going to develop the load processor by having code adding one object per load type per zone. A tentative 'Title Case' naming convention is going to be used, following geomeppy's way of naming surfaces and zones
2. In the meantime, Yunyang is going to look into the HVAV tempaltes, more specifically, the input needs and importances of the following two types of HVAC tempaltes

```
IDF,HVACTemplate:Zone:PTAC,,,autosize,autosize,,,,Flow/Person, .00944,,,,,DrawThrough, .7, 75, .9,SingleSpeedDX,,autosize,autosize, 3,Electric,,autosize, .8,,,SupplyAirTemperature, 14, 11.11,SupplyAirTemperature, 50, 30,,,None,,autosize,None;

IDF,HVACTemplate:Zone:PTHP,,,autosize,autosize,,,,Flow/Person, .00944,,,,,DrawThrough, .7, 75, .9,SingleSpeedDX,,autosize,autosize, 3,SingleSpeedDXHeatPump,,autosize, 2.75,-8, 5,ReverseCycle,Timed, .058333,Electric,,autosize, 21, .8,,,SupplyAirTemperature, 14, 11.11,SupplyAirTemperature, 50, 30,,,None,,autosize,None;
```

3. When item 1 is finished, Jerry will work with Yunyang to figure out how to use Yunyang's deatailed occupancy schedule in the model through the schedule processor. The initial development will be having universal schedule for everything. Adding different schedules for different things will be a later task.
4. When the above two items are finished, using the hvac template to generate single zone system should be a straightforward implementation of the hvac processor.

Some development sidenotes:

1. When devloping mdoeling strategies, we think mainly about what things we want to model for each processor. We assume and stick to a certain set of data / information inputs without considering whether Comcheck / CBECS can provide them at the needed level of detail or not. The transformation from dataset features to the inputs needed by the modeling strategies will be the job of the dataset interfaces, acting like adaptors / wrappers. They will be developed later when we have more details about the data and our model generation implementation.
2. We will not have simultaneous processors being coded at the same time. The three of us will work together to tackle the processors one by one sequentially.
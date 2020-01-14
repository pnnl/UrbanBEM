## Meeting minutes for discussion on 01/14/2020

### About "Lego" modeling approach

- We had two different "Lego" modeling approach on the table
  1. Simplify and disassemble a building model into multiple bricks according to thermal zones and for each brick, creating a separate model (idf) and run simulation against
  2. Simplify and disassemble a building model into multiple bricks according to thermal zones, but all bricks are still inside one model (idf) and will be simulated together
     We lean towards the second approach
- If everything is a single zone system, then either of the above two approaches works. If it is a multi-zone system, then approach 1 won't work. Within the same idf, we can assign multiple zones in the same HVAC system.

### Do we want to have pre-simulated load profiles to answer questions

- This depends on the application.

### Benefits of the proposed modeling approach

- Comparing with ground up case-specific modelling (i.e. modeling in our prototypes), in this project, we do on the fly zoning and would have more flexibility. Easier to troubleshooting, and do benchmarking
- Comparing with existing simulation-based benchmarking tool. Our lego modeling approach is more sophisticated and is expected to yield more accurate results.
  - This needs to be confirmed.
  - Comparing with Comcheck?
  - Some earlier benchmarking tool would build a simple rectangle space model to simulate the baseline energy usage.

### Potential issues

- Inter-building shading: LBNL's Tianhen Hong developed an EP feature to capture the inter-bldg shading impact. More detailed information is not acquired yet.
- Inter-building airflow impact: Unknown knowledge

### Zoning heuristics

- Rules in the ASHRAE appendix C is probably a better resource than digging the Comcheck source code.
- Jerry will have a look at the appendix and Jian will lead Jerry on it later.

### More

- Yunyang did a review on existing large scale modeling approaches, this is potentially very helpful and we shall later have him involved in the project. (Jian will decide when to include him)
- Since several third-party software, e.g. Eppy/Geomeppy, Modelkit, openstudio, has templates or routines to automatically inject HVAC systems in to the model. We shall aim at developing a set of interfaces to talk to these tools when buildjing our models. This can also be a selling point especially since we are building and showcasing a framework

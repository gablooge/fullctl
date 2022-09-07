# Service Bridge

The fullctl service bridge is a way for fullctl services to exchange information seamlessly using the RESTful api.

## ServiceBridgeModel

The `ServiceBridgeModel` base class allows a django model to have a main reference at another service.

This reference can then be used to populate data, either once, or continuously if the reference is flagged as the
source for truth.

## ServiceBridgeAction

ServiceBridgeAction allows one to add database controlled additional pull or push actions for a model.

These can be used to push data from the model to its references, or pull in additional data from secondary references.


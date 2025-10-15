# Auto generated models

We have a type definition using openapi V2 for our models. However they are not currently totally in line with our actual server implmentation. To make sure the SDK works while we transition our models to use the OpenAPI spec, we have two folders in thid directory:

- [_hand_rolled](./_hand_rolled) These are manually maintained api objects. We keep models here until the API is returning the correct spec.
- [_generated](./_generated/) These are auto generated api objects. We keep them in a separate directory.

We use this directory to import the correct model for eacallh request/response objects and to make it easier for our users to just use the correct object. While we manage the transition.

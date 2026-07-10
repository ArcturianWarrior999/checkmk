# Naming convention for concepts with discovery capabilities

For each concept, keyed on its singular base name:

| Name                | Description                                |
| ------------------- | ------------------------------------------ |
| `<concept>_abc`     | the abstraction (ABC + associated types)   |
| `<concept>_builder` | discovery + construction (factory/builder) |
| `<concept>s/`       | implementations, as a namespace package    |

Abstraction and construction modules live outside the implementations namespace package.

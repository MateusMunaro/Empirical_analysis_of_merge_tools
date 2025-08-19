import javax.persistence.*;
import com.fasterxml.jackson.annotation.*;

@
<<<<<<< ./senarios_merge_base/JDime/scenario_41/left/customer.java
Entity
=======
JsonInclude
>>>>>>> ./senarios_merge_base/JDime/scenario_41/right/customer.java
(value = JsonInclude.Include.NON_NULL) @
<<<<<<< ./senarios_merge_base/JDime/scenario_41/left/customer.java
Table
=======
JsonPropertyOrder
>>>>>>> ./senarios_merge_base/JDime/scenario_41/right/customer.java
(
<<<<<<< ./senarios_merge_base/JDime/scenario_41/left/customer.java
name = "customers"
=======
value = { "id", "name", "email" }
>>>>>>> ./senarios_merge_base/JDime/scenario_41/right/customer.java
) public class Customer {
  @
<<<<<<< ./senarios_merge_base/JDime/scenario_41/left/customer.java
  Id
=======
  JsonProperty
>>>>>>> ./senarios_merge_base/JDime/scenario_41/right/customer.java
  (value = "customer_id") @GeneratedValue(strategy = GenerationType.IDENTITY) private Long id;

  @
<<<<<<< ./senarios_merge_base/JDime/scenario_41/left/customer.java
  Column
=======
  JsonProperty
>>>>>>> ./senarios_merge_base/JDime/scenario_41/right/customer.java
  (
<<<<<<< ./senarios_merge_base/JDime/scenario_41/left/customer.java
  nullable = false
=======
  value = "full_name"
>>>>>>> ./senarios_merge_base/JDime/scenario_41/right/customer.java
  , length = 100) private String name;

  @
<<<<<<< ./senarios_merge_base/JDime/scenario_41/left/customer.java
  Column
=======
  JsonProperty
>>>>>>> ./senarios_merge_base/JDime/scenario_41/right/customer.java
  (
<<<<<<< ./senarios_merge_base/JDime/scenario_41/left/customer.java
  unique = true
=======
  value = "email_address"
>>>>>>> ./senarios_merge_base/JDime/scenario_41/right/customer.java
  ) @JsonIgnore private String email;
}
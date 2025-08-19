import com.fasterxml.jackson.annotation.*;

import javax.persistence.*;

<<<<<<< ours
@Entity
@Table(name = "customers")
=======
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({"id", "name", "email"})
>>>>>>> theirs
public class Customer {
<<<<<<< ours
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
=======
    @JsonProperty("customer_id")
>>>>>>> theirs
    private Long id;
    
<<<<<<< ours
    @Column(nullable = false, length = 100)
=======
    @JsonProperty("full_name")
>>>>>>> theirs
    private String name;
    
<<<<<<< ours
    @Column(unique = true)
=======
    @JsonProperty("email_address")
    @JsonIgnore
>>>>>>> theirs
    private String email;
}
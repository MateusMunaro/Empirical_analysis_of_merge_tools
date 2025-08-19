import javax.persistence.*; import com.fasterxml.jackson.annotation.*; 

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({"id", "name", "email"})
public  class  Customer {
	
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

	
    
    @JsonProperty("full_name")
    private String name;

	
    
    @Column(unique = true)
    private String email;


}

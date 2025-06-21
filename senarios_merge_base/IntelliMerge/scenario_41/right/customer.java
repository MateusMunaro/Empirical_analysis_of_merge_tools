import com.fasterxml.jackson.annotation.*;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({"id", "name", "email"})
public class Customer {
    @JsonProperty("customer_id")
    private Long id;
    
    @JsonProperty("full_name")
    private String name;
    
    @JsonProperty("email_address")
    @JsonIgnore
    private String email;
}
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class PersonService {
    private Map<Integer, Client> personDB;
    
    public PersonService() {
        this.personDB = new HashMap<>();
    }
    
    public Client save(Client person) {
        personDB.put(person.getId(), person);
        return person;
    }
    
    public Client findById(int id) {
        return personDB.get(id);
    }
    
    public List<Client> findAll() {
        return new ArrayList<>(personDB.values());
    }
    
    public void delete(int id) {
        personDB.remove(id);
    }
    
    public boolean exists(int id) {
        return personDB.containsKey(id);
    }
    
    public Client update(Client person) {
        if (exists(person.getId())) {
            return save(person);
        }
        return null;
    }
}
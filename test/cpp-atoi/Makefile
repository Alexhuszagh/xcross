.PHONY: all
all: atoi

.PHONY: clean
clean:
	rm -f atoi.o atoi

OBJECTS=atoi.o
atoi: $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(OBJECTS) -o atoi $(LDFLAGS)

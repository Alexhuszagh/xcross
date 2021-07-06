.PHONY: all
all: helloworld

.PHONY: clean
clean:
	rm -f helloworld.o helloworld

OBJECTS=helloworld.o
helloworld: $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(OBJECTS) -o helloworld $(LDFLAGS)

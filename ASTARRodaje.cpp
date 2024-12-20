#include <iostream>
#include <utility>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <unordered_map>
#include <limits>  // For std::numeric_limits
#include <chrono>
using namespace std;

struct Cell
{
    pair<int, int> coordinates;
    char state; // type of the cell: yellow, gray, white
    bool operator==(const Cell& other) const {
        return coordinates == other.coordinates && state == other.state;
    }
};

namespace std {
    template <>
    struct hash<Cell> {
        size_t operator()(const Cell& cell) const {
            size_t hash_value = 0;

            // Hash coordinates (pair of ints)
            hash_value ^= hash<int>()(cell.coordinates.first) << 1;
            hash_value ^= hash<int>()(cell.coordinates.second) << 2;

            // Hash state (character)
            hash_value ^= hash<char>()(cell.state) << 3;

            return hash_value;
        }
    };
}

struct Aircraft {
    int id;
    Cell initialPosition;
    Cell runwayPosition;
    Cell currentPosition;
    int time;
    bool operator==(const Aircraft& other) const {
        return id == other.id && initialPosition == other.initialPosition
        && runwayPosition == other.runwayPosition &&
        currentPosition == other.currentPosition && time == other.time;
    }
};

namespace std {
    template <>
    struct hash<Aircraft> {
        size_t operator()(const Aircraft& aircraft) const {
            size_t hash_value = 0;

            // Hash the aircraft id
            hash_value ^= hash<int>()(aircraft.id) << 1;

            // Hash the Cell objects
            hash_value ^= hash<Cell>()(aircraft.initialPosition) << 2;
            hash_value ^= hash<Cell>()(aircraft.runwayPosition) << 3;
            hash_value ^= hash<Cell>()(aircraft.currentPosition) << 4;

            // Hash the time
            hash_value ^= hash<int>()(aircraft.time) << 5;

            return hash_value;
        }
    };
}

struct State {
    // stores all planes with all their data including currect position
    // mostly by the positions the state is defined
    vector<Aircraft> aircrafts;
    int g;
    double h;

    double f() const{
        return g + h;
    }
    bool operator<(const State& other) const {
        return f() < other.f();
    }

    bool operator==(const State& other) const {
        if (aircrafts.size() != other.aircrafts.size())
            return false;
        for (int i=0; i<aircrafts.size(); i++){
            if (!(aircrafts[i] == other.aircrafts[i]))
                return false;
        }
        return true;
    }
    State(): aircrafts(), g(0), h(std::numeric_limits<int>::max()){}
    State(const vector<Aircraft>& aircrafts, int g, int h)
            : aircrafts(aircrafts), g(g), h(h) {}
};

namespace std {
    template <>
    struct hash<State> {
        size_t operator()(const State& state) const {
            size_t hash_value = 0;

            // Hash the aircrafts vector (using the hash for Aircraft)
            for (const auto& aircraft : state.aircrafts) {
                hash_value ^= hash<Aircraft>()(aircraft) << 1;
            }

            // Hash g, h, and f (int values)
            hash_value ^= hash<int>()(state.g) << 2;
            hash_value ^= hash<int>()(state.h) << 3;

            return hash_value;
        }
    };
}

bool readMapCSV(const std::string& filename, vector<Aircraft>& aircrafts, vector <vector<Cell> > &map){
    /*
     * read csv file that stores data about plane as well as map
     */
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Error opening file " << filename << endl;
        return false;
    }

    string line;
    
    // Read the number of aircraft (n)
    int n;
    getline(file, line);
    istringstream(line) >> n;

    // Read the aircraft positions (next n lines)
    aircrafts.resize(n);
    for (int i = 0; i < n; ++i) {
        getline(file, line);
        istringstream ss(line);
        char ch; // To read the parentheses and comas
        aircrafts[i].id = i;
        ss >> ch >> aircrafts[i].initialPosition.coordinates.first >> ch >> aircrafts[i].initialPosition.coordinates.second >> ch;
        aircrafts[i].initialPosition.state = 'B';
        aircrafts[i].runwayPosition.state = 'B';
        aircrafts[i].currentPosition = aircrafts[i].initialPosition;
        ss >> ch >> aircrafts[i].runwayPosition.coordinates.first >> ch >> aircrafts[i].runwayPosition.coordinates.second >> ch;
        aircrafts[i].time = 0;
    }

    // Read the map matrix
    map.clear();
    int r = 0;
    int c = 0;
    while (std::getline(file, line)) {
        std::vector<Cell> row;
        std::istringstream ss(line);
        std::string cell;
        c = 0;
        while (std::getline(ss, cell, ';')) {
            Cell cell1;
            cell1.coordinates.first = r;
            cell1.coordinates.second = c;
            cell1.state = cell[0];
            row.push_back(cell1);
            c++;
        }
        r++;
        map.push_back(row);
    }

    file.close();
    return true;
}

vector <Cell> getNeighbours(Cell cell, vector< vector<Cell> > &map){
    /*
     * return all possible neighbour cells to which it is possible to move
     */
    vector <Cell> neighbours;
    int nx = 0, ny = 0;
    int directions [5][2] = {{0, 1}, {0, -1}, {1, 0}, {-1, 0}, {0, 0}};

    for (int i=0; i<4; i++){
        nx = cell.coordinates.first + directions[i][0];
        ny = cell.coordinates.second + directions[i][1];
        if (0 <= nx && nx < map.size() && 0 <= ny && ny < map[0].size() && map[nx][ny].state != 'G')
            // cannot move to gray block or ones out of map
            neighbours.push_back(map[nx][ny]);
    }
    // check if the cell itself yellow, it cannot be a neighbour, in sense that plane should be moved from this cell
    if (cell.state != 'A')
        neighbours.push_back(map[cell.coordinates.first][cell.coordinates.second]); // so we can wait if it is not yellow
    return neighbours;

}

double manhattanDistance(Aircraft aircraft){
    /*
     * compute manhattan distance from current position to the goal one
     */
    return abs(aircraft.currentPosition.coordinates.first - aircraft.runwayPosition.coordinates.first)
    + abs(aircraft.currentPosition.coordinates.second - aircraft.runwayPosition.coordinates.second);
}

double euclideanDistance(Aircraft aircraft) {
    /*
     * compute Euclidean distance from the current position to the goal one
     */
    int x1 = aircraft.currentPosition.coordinates.first, y1 = aircraft.currentPosition.coordinates.second;
    int x2 = aircraft.runwayPosition.coordinates.first, y2 = aircraft.runwayPosition.coordinates.second;
    double distance = std::sqrt(std::pow(x2 - x1, 2) + std::pow(y2 - y1, 2));
    return distance;
}

double getHeuristic(State state, int heuristic){
    /*
     * get heuristics for the state as maximum of manhattan/Euclidean distances of each plane
     */
    double max_distance = 0;
    for (auto aircraft: state.aircrafts){
        if (manhattanDistance(aircraft) > max_distance){
            if (heuristic == 1)
                max_distance = manhattanDistance(aircraft);
            else
                max_distance = euclideanDistance(aircraft);
        }
    }
    return max_distance;
}

bool isGoal(State& state){
    /*
     * check if the current state is a goal one
     */
    bool goal = true;
    for (auto aircraft: state.aircrafts){
        if (aircraft.currentPosition.coordinates != aircraft.runwayPosition.coordinates)
            goal = false;
    }
    return goal;
}

int getMinTime(State state){
    /*
     * get maximum time moment among all planes
     */
    int min_time = state.aircrafts[0].time;
    for (auto plane: state.aircrafts){
        if (plane.time < min_time)
            min_time = plane.time;
    }
    return min_time;
}

int getMaxTime(State current){
    /*
     * get maximum time moment among all planes
     */
    int max_time = 0;
    for (auto plane: current.aircrafts){
        if (plane.time > max_time)
            max_time = plane.time;
    }
    return max_time;
}
vector < State > getNeighbourState(State &current, vector<vector<Cell> > &map, int heuristic){
    /*
     * return vector of neighbour states sorted by the function f(expected 'price' of getting to goal from start through node)
     * neighbour states are the ones that can be reached from the current one in one move that is allowed
     */
    vector<State> neighbourStates;

    int min_time = getMinTime(current);  // compute minimum time moment
    vector <Cell> neighboursCells;

    Aircraft plane;
    for (int i=0; i<current.aircrafts.size(); i++){  // go through every plane
        State state = current;
        plane = current.aircrafts[i];
        if (plane.time > min_time)  // if plane is in 1 time distance, we skip it
            continue;
        if (plane.currentPosition == plane.runwayPosition) // if some plane is already at its goal, no need to move it
            neighboursCells.push_back(plane.currentPosition);
        else {
            // if not, generate all states of all possible movements of plane
            neighboursCells = getNeighbours(plane.currentPosition, map);
            for (auto planeTmp: current.aircrafts){
                if (plane.id != planeTmp.id){
                    neighboursCells.erase( // if there is already plane at any neighbour, plane cannot move there
                            remove(neighboursCells.begin(), neighboursCells.end(), planeTmp.currentPosition),
                            neighboursCells.end());
                }
            }
        }
        // add them to neighbourStates
        plane.time++;
        for (Cell cell: neighboursCells){
            plane.currentPosition = cell;
            state.aircrafts[i] = plane;
            state.g = getMaxTime(state);
            state.h = getHeuristic(state, heuristic);
            neighbourStates.push_back(state);
        }
        // go to the following plane and repeat it

    }
    // after adding all possible states, sort it
    sort(neighbourStates.begin(), neighbourStates.end());
    return neighbourStates;
}

vector<State> merge(vector<State> &first, vector<State> &second){
    /*
     * merge two sorted vectors by value of f of each state
     * output vector will be sorted in increasing order
     */
    vector<State> merged(first.size() + second.size());
    int i = 0;
    int j = 0;
    int k = 0;
    while (i != first.size() && j != second.size()){
        if (first[i] < second[j])
            merged[k++] = first[i++];
        else
            merged[k++] = second[j++];
    }
    if (i != first.size()){
        while (i != first.size())
            merged[k++] = first[i++];
    }
    if (j != second.size()){
        while (j != second.size())
            merged[k++] = second[j++];
    }
    return merged;

}

vector<State> a_star(vector <vector<Cell> > &map, vector<Aircraft>& aircrafts, int heuristic, unsigned long& nodes){
    /*
     * perform A* search for finding the routs for aircrafts on map using provided heuristic
     * each plane has its initial and goal location
     * no plane can be in the same map cell simultaneously, or can swap positions
     */
    vector< State > openSet;  // used for states we opened
    vector< State > closedSet;  // used for states we already transited(expanded)
    State tmp;
    tmp.aircrafts = aircrafts; // initial state
    tmp.h = getHeuristic(tmp, heuristic);
    openSet.push_back(tmp);
    unordered_map<State, State> cameFrom; // to keep track from which state we got to this one
    vector<State> neighbours;
    bool found = false;
    State final;
    while (!openSet.empty() && !found){
        // openSet will be on purpose already sorted by f
        State current = openSet.front();  // get state with smallest f
        openSet.erase(openSet.begin());
        if (isGoal(current)) { // check if it is goal
            final = current;
            break;
        }
        neighbours = getNeighbourState(current, map, heuristic);  // generate all neighbours states(one plane is moved)
        for (State neighbour: neighbours){
            auto it = find(closedSet.begin(), closedSet.end(), neighbour);
            if (it != closedSet.end()) // if neighbour is in closed set, we do not consider it
                neighbours.erase(find(neighbours.begin(), neighbours.end(), neighbour));
            else {
                it = find(openSet.begin(), openSet.end(), neighbour);
                if (it != openSet.end()) { // if it is in open and if we get to it faster, set new g
                    if (it->g > neighbour.g) {
                        it->g = neighbour.g;
                        cameFrom[neighbour] = current;
                    }
                    // remove it from neighbours not to consider it later
                    neighbours.erase(find(neighbours.begin(), neighbours.end(), neighbour));
                }
            }

        }
        for (int i=0; i<neighbours.size(); i++){ // for every neighbour state set one from which we got there
            cameFrom[neighbours[i]] = current;
            if (isGoal(neighbours[i])){
                found = true; // if neighbour state is a goal one, end while loop and stop
                final = neighbours[i];
                break;
            }
        }
        // merge left neighbours with open set for later to take state with smallest f
        openSet = merge(openSet, neighbours); // merge and store result in open set
        closedSet.push_back(current); // mark as visited
    }
    vector<State> path;
    tmp = final;
    bool state = false;
    while (!state){ // get states sequence from final state to the initial one
        path.push_back(tmp);
        if (cameFrom[tmp].aircrafts == aircrafts){
            path.push_back(cameFrom[tmp]);
            state = true;
        }
        tmp = cameFrom[tmp];
    }
    // in case some planes are already at goal but in time moment earlier
    // time is increased so each plane at final state is at the same time moment
    if (getMaxTime(path[0]) != getMinTime(path[0])){
        for (int i=0; i<path[0].aircrafts.size(); i++){
            if (path[0].aircrafts[i].time != getMaxTime(path[0]))
                path[0].aircrafts[i].time++;
        }
    }
    reverse(path.begin(), path.end()); // reverse it to have from initial to final one
    nodes = closedSet.size() + openSet.size();
    return path;

}

void printPair(ofstream& outFile, pair<int, int> p){
    /*
     * print pair to the output stream
     */
    outFile << "(" << p.first << ", " << p.second << ")";
}

void getOperation(ofstream& outFile, pair<int, int> before, pair<int, int> after){
    /*
     * print operation performed moving from one coordinate to another to the output stream
     */
    if (after.first == before.first && after.second == before.second) {
        outFile << " w "; // Both pairs are the same
    } else if (after.first < before.first) {
        outFile << " ↑ " ; // after is above before
    } else if (after.first > before.first) {
        outFile << " ↓ " ; // after is below before
    } else if (after.second < before.second) {
        outFile << " ← " ; // after is to the left from before
    } else if (after.second > before.second) {
        outFile << " → " ; // after is to the right from before
    }
}

bool output(string& outputFilePath, vector<State> &path){
    /*
     * output to the file the path in specific format
     * each line corresponds to path of certain plain
     * positions at time t are shown as location tuple
     * and the movement of plane is shown by arrows
     */
    ofstream outFile(outputFilePath);
    if (!outFile) {
        cerr << "Error opening file for writing!" << std::endl;
        return false; // Exit with error code
    }

    for (int i=0; i<path[0].aircrafts.size(); i++){
        printPair(outFile, path[0].aircrafts[i].initialPosition.coordinates);
        for (int j=1; j<path.size(); j++){
            if (path[j].aircrafts[i].time != path[j-1].aircrafts[i].time) { // if plane moved in time
                getOperation(outFile, path[j-1].aircrafts[i].currentPosition.coordinates,
                             path[j].aircrafts[i].currentPosition.coordinates);
                printPair(outFile, path[j].aircrafts[i].currentPosition.coordinates);
            }
        }
        outFile << endl;
    }

    // Close the file
    outFile.close();
    return true;
}

int main(int argc, char* argv[]){
    // Check if the correct number of arguments is provided
    if (argc != 3) {
        cerr << "Usage: " << argv[0] << " <file_path> <arg>\n";
        return 1; // Exit with error code
    }
    string filePath = argv[1];
    int heuristic;
    try {
        heuristic = std::stoi(argv[2]);
    } catch (const std::invalid_argument& e) {
        cerr << "Error: Argument must be an integer.\n";
        return 1; // Exit with error code
    } catch (const std::out_of_range& e) {
        cerr << "Error: Argument out of range for an integer.\n";
        return 1; // Exit with error code
    }
    vector<Aircraft> aircrafts;  // vector to store planes
    vector<vector<Cell> > map;

    if (!readMapCSV(filePath, aircrafts, map))
        cerr << "Failed to read the map file.\n";


    unsigned long nodes = 0;
    auto start = chrono::high_resolution_clock::now();
    vector<State> path = a_star(map, aircrafts, heuristic, nodes);
    auto end = chrono::high_resolution_clock::now();

    // Calculate the duration
    chrono::duration<double> duration = end - start;

    string outputFilePath = filePath;
    size_t lastDot = outputFilePath.find_last_of('.');
    outputFilePath.replace(lastDot, string::npos, "-" + to_string(heuristic) + ".output");


    if (!output(outputFilePath, path))
        cerr << "Failed to write the map file.\n";


    string statFilePath = filePath;
    lastDot = statFilePath.find_last_of('.');
    statFilePath.replace(lastDot, string::npos, "-" + to_string(heuristic) + ".stat");

    ofstream outFile(statFilePath);
    if (!outFile) {
        cerr << "Error opening file for stats!" << std::endl;
        return 1;
    }
    outFile << "Total time: " << duration.count() << 's' << endl;
    outFile << "Makespan: " << path.size() << endl; // States to reach goal
    outFile << "Init heuristic: " << path[0].h << endl;
    outFile << "Nodes expanded: " << nodes << endl;
    outFile.close();

    return 0;
}
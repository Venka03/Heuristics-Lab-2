#include <iostream>
#include <utility>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <map>
using namespace std;

struct Cell
{
    pair<int, int> coordinates;
    char state; // type of the cell: yellow, gray, white
};

struct Aircraft {
    int id;
    Cell initialPosition;
    Cell runwayPosition;
    Cell currentPosition;
    int time;
};


bool readMapCSV(const std::string& filename, int& n, vector<Aircraft>& aircrafts, vector <vector<Cell> > &map){
    ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error opening file " << filename << std::endl;
        return false;
    }

    std::string line;
    
    // Read the number of aircraft (n)
    std::getline(file, line);
    std::istringstream(line) >> n;

    // Read the aircraft positions (next n lines)
    aircrafts.resize(n);
    for (int i = 0; i < n; ++i) {
        std::getline(file, line);
        std::istringstream ss(line);
        char ch; // To read the parentheses
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
    vector <Cell> neighbours;
    int nx = 0, ny = 0;
    int directions [4][2] = {{0, 1}, {0, -1}, {1, 0}, {-1, 0}};
    for (auto direction: directions){
        //if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] != 'G':
        //neighbors.append((nx, ny))
        nx = cell.coordinates.first + direction[0];
        ny = cell.coordinates.second + direction[1];
        if (0 <= nx && nx < map.size() && 0 <= ny && ny < map[0].size() && map[nx][ny].state != 'G')
            neighbours.push_back(map[nx][ny]);
    }
    return neighbours;

}

void a_star(vector <vector<Cell> > &map, vector<Aircraft>& aircrafts){
    vector< vector< Aircraft > > openSet;
    openSet.push_back(aircrafts); // use another data type for this
    int time = 0; // to keep the lowest time of planes
    std::map<Cell, Cell> cameFrom;
    // should be using some while loop
    vector<Aircraft> current = openSet.front();
    // add if that will check is current is final or not

    for (auto plane: current){
        if (plane.time == time){ // to avoid moving plane to t+2 when there are planes at t
            vector<Cell> neighbours = getNeighbours(plane.currentPosition, map);
            openSet.erase(openSet.begin());
            for (auto neighbour: neighbours){
                int tentative_gScore = plane.time + 1;
                //if (tentative_gScore < )
            }
        }


    }



}

int main(){
    string filename = "map.csv";
    int n;
    vector<Aircraft> aircrafts;
    vector<vector<Cell> > map;

    if (readMapCSV(filename, n, aircrafts, map)) {
        cout << "Fine\n";
    } else {
        cerr << "Failed to read the map file.\n";
    }

    a_star(map, aircrafts);

    return 0;
}
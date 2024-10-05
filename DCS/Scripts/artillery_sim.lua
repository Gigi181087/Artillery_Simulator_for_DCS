package.path = package.path .. ";" .. lfs.currentdir() .. "\\LuaSocket\\?.lua"
package.cpath = package.cpath .. ";" .. lfs.currentdir() .. "\\LuaSocket\\?.dll"
local socket = require("socket")
local artillery_simulator_connection_socket = nil
local is_connected = false
local last_time = 0
local JSON

local function initalize_module()
    local test, err = (loadfile "Scripts\\JSON.lua") ()
    
    if not test then
        print("Fehler beim Laden der JSON-Bibliothek: " .. err)
        
        return
    end

    JSON = test
end

local function connect_to_server()

    if not artillery_simulator_connection_socket then
        artillery_simulator_connection_socket = socket.tcp()
        artillery_simulator_connection_socket:settimeout(0)
    end

    host = "localhost"
    port = 15000
    local result, error = artillery_simulator_connection_socket:connect(host, port)

    if result then
        trigger.action.outText("Connected!", 10)
        artillery_simulator_connection_socket:setoption("tcp-nodelay", true)
        is_connected = true

    elseif error == "already connected" then
        trigger.action.outText("Connected!", 10)
        is_connected = true
    end

end

local function close_socket()

    if artillery_simulator_connection_socket then
        artillery_simulator_connection_socket:close()
        artillery_simulator_connection_socket = nil
        is_connected = false
    end

    return
end

local function get_vector(position, azimuth, elevation)
    local azimuth_rad = math.rad(azimuth)
    local elevation_rad = math.rad(elevation)

    -- calculate normalized vector
    local vector = {
        x = math.cos(elevation_rad) * math.cos(azimuth_rad),
        y = math.sin(-elevation_rad),
        z = math.cos(elevation_rad) * math.sin(azimuth_rad)
    }

    return vector
end

local function calculate_early_impact(start_position, vector)
    -- get point in the distance
    local distance_point = {
        x = start_position.x - vector.x * 2000,
        y = start_position.y - vector.y * 2000,
        z = start_position.z - vector.z * 2000
    }

    return land.getIP(distance_point, vector, 2000)
end

local function calculate_late_impact(start_position, vector)

    return land.getIP(start_position, vector, 2000)
end    
    
    

local function execute_simulated_shot(shot)
    trigger.action.outText("Executing shot!", 10)
    local caliber = shot["caliber"]
    local fuze = shot["fuze"]
    -- function to calculate internal coordinates from mgrs
    local latitude, longitude = coord.MGRStoLL(shot["location"]["coordinate"])
    local coordinate = coord.LLtoLO(latitude, longitude, shot["location"]["elevation"])
    
    local vector = get_vector(coordinate, shot["direction"], shot["impact_angle"])

    if fuze == "airburst" then
        coordinate.y = coordinate.y - 8

    end

    -- check for early impact
    local impact_coordinate = calculate_early_impact(coordinate, vector)

    if impact_coordinate == nil then
        trigger.action.outText("No early impact!", 10)

        if fuze ~= "time" then
            impact_coordinate = calculate_late_impact(coordinate, vector)
            
        else
            impact_coordinate = coordinate

        end

        if impact_coordinate == nil then
            trigger.action.outText("Error, impact ccordinate is nil!", 10)
        end
        
    end

    if shot["ammunition_type"] == "high_explosive" then

        if fuze == "airburst" then
            impact_coordinate.y = impact_coordinate.y + 8

        elseif fuze == "delay" then
            impact_coordinate.y = impact_coordinate.y - 3

        end

        trigger.action.outText("Latitude: " .. impact_coordinate.x .. " Longitude: " .. impact_coordinate.z .. " Elevation: " .. impact_coordinate.y, 10)
        trigger.action.explosion(impact_coordinate, caliber)

    elseif shot["ammunition_type"] == "illumination" then

        trigger.action.illuminationBomb(coordinate)

    elseif shot["ammunition_type"] == "smoke" then
        trigger.action.smoke(coordinate, trigger.smokeColor.White)

    end

    return nil
end

local function process_simulated_shot(shot)
    timer.scheduleFunction(execute_simulated_shot, shot, shot["time_fired"] + shot["time_of_flight"] - timer.getTime0())

    return
end

local function send_mission_time()

    if not is_connected then

        return
    end
    
    if is_connected then
        local current_mission_time = timer.getAbsTime()

        if current_mission_time ~= last_time then
            local data = {
                Missiontime = current_mission_time
            }
            local json_string = JSON:encode(data)
            result, error = artillery_simulator_connection_socket:send(json_string .. "\n")

            if error == "closed" then
                trigger.action.outText("Connection lost!", 10)
                close_socket()
            end

            last_time = current_mission_time
        end

    end

    return
end

local function receive_data()

    if not is_connected then

        return
    end

    while true do
        data, error = artillery_simulator_connection_socket:receive()

        if data then
            trigger.action.outText(data, 10)
            local message = JSON:decode(data)

            if message["simulated_shot"] then
                process_simulated_shot(message["simulated_shot"])
            end

        elseif error == 'timeout' then

            break

        elseif error == "closed" then
            trigger.action.outText("Connection lost!", 10)
            close_socket()

            break
        end
    end
end

local function loop()

    if not is_connected then
        connect_to_server()

        return timer.getTime() + 2
    end

    send_mission_time()
    receive_data()

    return timer.getTime() + 0.05
end

initalize_module()
timer.scheduleFunction(loop, nil, timer.getTime() + 2)
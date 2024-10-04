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

local function execute_simulated_shot(shot)
    local caliber = shot["caliber"]
    
    -- function to calculate internal coordinates from mgrs
    local latitude, longitude = coord.MGRStoLL(shot["location"]["coordinate"])
    local coordinate = coord.LLtoLO(latitude, longitude)
    coordinate.y = land.getHeight({x = coordinate.x, y = coordinate.z})
    trigger.action.outText(coordinate.y, 10)    

    if shot["ammunition_type"] == "high_explosive" then

        if shot["fuze"] == "impact" then
            coordinate.y = coordinate.y

        elseif shot["fuze"] == "airburst" then
            coordinate.y = coordinate.y + 10
        end

        trigger.action.explosion(coordinate, caliber)

    elseif shot["ammunition_type"] == "illumination" then

        if shot["fuze"] == "time" then
            local elevation = shot["location"]["elevation"]

            if elevation > coordinate.y then
                coordinate.y = elevation
            end

        end

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
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
    trigger.action.outText("Attempting connection", 1)

    if not artillery_simulator_connection_socket then
        artillery_simulator_connection_socket = socket.tcp()
        artillery_simulator_connection_socket:settimeout(0)
    end

    host = "localhost"
    port = 15000
    local result, error = artillery_simulator_connection_socket:connect(host, port)
    trigger.action.outText(error, 1)

    if result then
        trigger.action.outText("Connected!", 1)
        artillery_simulator_connection_socket:setoption("tcp-nodelay", true)
        is_connected = true

    elseif error == "already connected" then
        trigger.action.outText("Connected!", 1)
        is_connected = true
    
    else
        trigger.action.outText("Failed!", 1)

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
    local coordinate2d = {
        x = shot["Location"]["Latitude"], 
        z = shot["Location"]["Longitude"],
    }
    local elevation = land.getHeight(coordinate2d)
    local coordinate3d = {
        x = coordinate2d.x,
        z = coordinate2d.z,
        y = elevation
    }
    local caliber = shot["Caliber"]

    if shot["Ammunition Type"] == "high_explosive" then
        trigger.action.outText("Executing shot!", 5)
        trigger.action.explosion(coordinate3d, caliber)
    
    elseif shot["Ammunition Type"] == "high_explosive_air_burst" then
        trigger.action.outText("Executing Airburst!", 5)
        coordinate3d.y = coordinate3d.y + 30
        trigger.action.explosion(coordinate3d, caliber)

    elseif shot["Ammunition Type"] == "illumination" then
        trigger.action.outText("Executing Illumination!", 5)
        coordinate3d.y = coordinate3d.y + 600
        trigger.action.illuminationBomb(coordinate3d)

    elseif shot["Ammunition Type"] == "smoke" then
        trigger.action.outText("Executing Smoke!", 5)
        trigger.action.smoke(coordinate3d, trigger.smokeColor.White)
        
    end

    return nil
end

local function process_simulated_shot(shot)
    trigger.action.outText("Processing Shot", 1)
    timer.scheduleFunction(execute_simulated_shot, shot, shot["Time Fired"] + shot["Time Of Flight"] - timer.getTime0())

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

            if message["Simulated Shot"] then
                process_simulated_shot(message["Simulated Shot"])
            end

        elseif error == 'timeout' then

            break

        elseif error == "closed" then
            close_socket()

            break
        end
    end
end

local function loop()

    if not is_connected then
        connect_to_server()
    end

    send_mission_time()
    receive_data()

    return timer.getTime() + 0.05
end

initalize_module()
timer.scheduleFunction(loop, nil, timer.getTime() + 2)
# Artillery_Simulator_for_DCS

## Install
1. Download Package
2. In your DCS World (openBeta)/scripts/MssionScripting.lua delete (comment out) the sanitize codes
    --Initialization script for the Mission lua Environment (SSE)

    dofile('Scripts/ScriptingSystem.lua')
    
    --Sanitize Mission Scripting environment
    --This makes unavailable some unsecure functions. 
    --Mission downloaded from server to client may contain potentialy harmful lua code that may use these functions.
    --You can remove the code below and make availble these functions at your own risk.
    
    local function sanitizeModule(name)
    	_G[name] = nil
    	package.loaded[name] = nil
    end
    
    do
    	--sanitizeModule('os')
    	--sanitizeModule('io')
    	--sanitizeModule('lfs')
    	--_G['require'] = nil
    	--_G['loadlib'] = nil
    	--_G['package'] = nil
    end

3. in your DCS Mission create a new trigger.
4. Set it to Once and select "do script"
5. Select artillery_sim.lua in "/DCS/Scripts
6. Start "main.py" in "/src"
7. Start mission
8. Visit "localhost:5000" in your browser
9. enjoy!

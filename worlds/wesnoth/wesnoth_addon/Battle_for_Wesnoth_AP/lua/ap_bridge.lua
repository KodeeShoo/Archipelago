local bridge = {}

local function get_bridge_path()
    local explicit = wesnoth.get_variable("ap_bridge_file")
    if explicit and explicit ~= "" then
        return explicit
    end

    local ok, userprofile = pcall(os.getenv, "USERPROFILE")
    if ok and userprofile and userprofile ~= "" then
        return userprofile .. "\\Documents\\My Games\\WesnothAP\\bridge_state.json"
    end

    local userdata = wesnoth.game_config and wesnoth.game_config.user_data_dir
    if userdata and userdata ~= "" then
        return userdata .. "/WesnothAP/bridge_state.json"
    end

    return "bridge_state.json"
end

local function read_file(path)
    local ok, handle = pcall(io.open, path, "r")
    if not ok or not handle then
        return nil
    end
    local contents = handle:read("*a")
    handle:close()
    return contents
end

local function write_file(path, contents)
    local dir = path:match("^(.*)[/\\][^/\\]+$")
    if dir and dir ~= "" then
        pcall(function()
            if package.config:sub(1, 1) == "\\" then
                os.execute('mkdir "' .. dir .. '" >NUL 2>NUL')
            else
                os.execute('mkdir -p "' .. dir .. '" >/dev/null 2>/dev/null')
            end
        end)
    end

    local ok, handle = pcall(io.open, path, "w")
    if not ok or not handle then
        wesnoth.message("Archipelago", "Could not write bridge file: " .. path)
        return false
    end
    handle:write(contents)
    handle:close()
    return true
end

local function parse_array(contents, key)
    local values = {}
    if not contents then
        return values
    end

    local array_text = contents:match('"' .. key .. '"%s*:%s*%[(.-)%]')
    if not array_text then
        return values
    end

    for value in array_text:gmatch('"(.-)"') do
        value = value:gsub('\\"', '"'):gsub("\\\\", "\\")
        table.insert(values, value)
    end

    return values
end

local function parse_bool(contents, key)
    if not contents then
        return false
    end
    return contents:match('"' .. key .. '"%s*:%s*true') ~= nil
end

local function encode_array(values)
    local encoded = {}
    for _, value in ipairs(values) do
        value = tostring(value):gsub("\\", "\\\\"):gsub('"', '\\"')
        table.insert(encoded, '"' .. value .. '"')
    end
    return "[" .. table.concat(encoded, ", ") .. "]"
end

local function unique_sorted(values)
    local seen = {}
    local result = {}
    for _, value in ipairs(values) do
        if value ~= "" and not seen[value] then
            seen[value] = true
            table.insert(result, value)
        end
    end
    table.sort(result)
    return result
end

local function table_from_variable_array(name, field)
    local values = {}
    local count = wesnoth.get_variable(name .. ".length") or 0
    for index = 0, count - 1 do
        local value = wesnoth.get_variable(name .. "[" .. index .. "]." .. field)
        if value then
            table.insert(values, value)
        end
    end
    return values
end

local function write_variable_array(name, field, values)
    wesnoth.set_variable(name)
    for index, value in ipairs(values) do
        wesnoth.set_variable(name .. "[" .. (index - 1) .. "]." .. field, value)
    end
end

function bridge.load()
    local path = get_bridge_path()
    wesnoth.set_variable("ap_bridge_file", path)

    local contents = read_file(path)
    local checked = parse_array(contents, "checked_locations")
    local items = parse_array(contents, "received_items")

    write_variable_array("ap_checked_locations", "name", checked)
    write_variable_array("ap_received_items", "name", items)
    wesnoth.set_variable("ap_goal_complete", parse_bool(contents, "goal_complete") and "yes" or "no")
end

function bridge.save()
    local path = get_bridge_path()
    local checked = unique_sorted(table_from_variable_array("ap_checked_locations", "name"))
    local items = table_from_variable_array("ap_received_items", "name")
    local goal = wesnoth.get_variable("ap_goal_complete") == "yes"

    local contents = "{\n"
        .. '  "checked_locations": ' .. encode_array(checked) .. ",\n"
        .. '  "received_items": ' .. encode_array(items) .. ",\n"
        .. '  "goal_complete": ' .. tostring(goal) .. "\n"
        .. "}\n"

    write_file(path, contents)
end

function bridge.mark_location(name)
    bridge.load()
    local checked = table_from_variable_array("ap_checked_locations", "name")
    table.insert(checked, name)
    write_variable_array("ap_checked_locations", "name", unique_sorted(checked))
    bridge.save()
end

function bridge.has_item(name)
    bridge.load()
    local items = table_from_variable_array("ap_received_items", "name")
    for _, item in ipairs(items) do
        if item == name then
            return true
        end
    end
    return false
end

return bridge

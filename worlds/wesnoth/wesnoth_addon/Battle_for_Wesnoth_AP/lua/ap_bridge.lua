local bridge = {}

local ITEM_STATE_FILE = "~add-ons/Battle_for_Wesnoth_AP/ap_items.json"

local function get_filesystem()
    local ok, module = pcall(function()
        if rawget and _G then
            return rawget(_G, "filesystem")
        end
        return nil
    end)
    if ok then
        return module
    end
    return nil
end

local function read_file(path)
    local filesystem = get_filesystem()
    if not filesystem then
        return nil
    end

    local ok, contents = pcall(filesystem.read_file, path)
    if not ok then
        return nil
    end
    return contents
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

local function parse_string(contents, key)
    if not contents then
        return nil
    end

    local value = contents:match('"' .. key .. '"%s*:%s*"(.-)"')
    if not value then
        return nil
    end

    return value:gsub('\\"', '"'):gsub("\\\\", "\\")
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
    local contents = read_file(ITEM_STATE_FILE)
    local items = parse_array(contents, "received_items")
    local seed_name = parse_string(contents, "seed_name")
    write_variable_array("ap_received_items", "name", items)
    if seed_name and seed_name ~= "" then
        wesnoth.set_variable("ap_seed_name", seed_name)
    end
end

function bridge.save()
    -- Wesnoth add-ons do not have general-purpose write access from Lua.
    -- The Python client reads checks from autosaves instead.
end

function bridge.mark_location(name)
    bridge.load()
    local checked = table_from_variable_array("ap_checked_locations", "name")
    table.insert(checked, name)
    write_variable_array("ap_checked_locations", "name", unique_sorted(checked))
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

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
    if wml and wml.array_access then
        local ok, rows = pcall(wml.array_access.get, name)
        if ok and type(rows) == "table" then
            for _, row in ipairs(rows) do
                if row[field] then
                    table.insert(values, row[field])
                end
            end
            return values
        end
    end

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

local function write_chest_array(values)
    wesnoth.set_variable("ap_two_brothers_chests")
    for index, value in ipairs(values) do
        local name, scenario, x, y = value:match("^(.-)|(.-)|(%d+)|(%d+)$")
        if name and scenario and x and y then
            local prefix = "ap_two_brothers_chests[" .. (index - 1) .. "]"
            wesnoth.set_variable(prefix .. ".name", name)
            wesnoth.set_variable(prefix .. ".scenario", scenario)
            wesnoth.set_variable(prefix .. ".x", tonumber(x))
            wesnoth.set_variable(prefix .. ".y", tonumber(y))
        end
    end
end

local function write_location_reward_array(values)
    wesnoth.set_variable("ap_location_rewards")
    for index, value in ipairs(values) do
        local location, item, player = value:match("^(.-)|(.-)|(.-)$")
        if location and item and player then
            local prefix = "ap_location_rewards[" .. (index - 1) .. "]"
            wesnoth.set_variable(prefix .. ".location", location)
            wesnoth.set_variable(prefix .. ".item", item)
            wesnoth.set_variable(prefix .. ".player", player)
        end
    end
end

local function announce_new_items(items)
    local announced = table_from_variable_array("ap_announced_items", "name")
    if #items < #announced then
        return
    end
    for index = #announced + 1, #items do
        wesnoth.wml_actions.message {
            speaker = "narrator",
            message = "Archipelago item received: " .. items[index]
        }
    end
    write_variable_array("ap_announced_items", "name", items)
end

function bridge.load(announce_items)
    local contents = read_file(ITEM_STATE_FILE)
    local items = parse_array(contents, "received_items")
    local seed_name = parse_string(contents, "seed_name")
    local roster = parse_array(contents, "roster_units")
    local recruits = parse_array(contents, "unlocked_recruits")
    local attacks = parse_array(contents, "unlocked_attacks")
    local chests = parse_array(contents, "two_brothers_chests")
    local rewards = parse_array(contents, "location_rewards")
    write_variable_array("ap_received_items", "name", items)
    write_variable_array("ap_roster_units", "type", roster)
    write_variable_array("ap_unlocked_recruits", "type", recruits)
    write_variable_array("ap_unlocked_attacks", "name", attacks)
    write_chest_array(chests)
    write_location_reward_array(rewards)
    wesnoth.set_variable("ap_recruit_list", table.concat(recruits, ","))
    if announce_items then
        announce_new_items(items)
    end
    if seed_name and seed_name ~= "" then
        wesnoth.set_variable("ap_seed_name", seed_name)
    end
end

function bridge.save()
    -- Wesnoth add-ons do not have general-purpose write access from Lua.
    -- The Python client reads checks from autosaves instead.
end

function bridge.is_location_checked(name)
    local checked = table_from_variable_array("ap_checked_locations", "name")
    for _, location in ipairs(checked) do
        if location == name then
            return true
        end
    end
    return false
end

function bridge.location_reward_text(name)
    if not name then
        return nil
    end

    for _, value in ipairs(parse_array(read_file(ITEM_STATE_FILE), "location_rewards")) do
        local location, item, player = value:match("^(.-)|(.-)|(.-)$")
        if location == name and item and player then
            return item .. " for " .. player
        end
    end

    if wml and wml.array_access then
        local ok, rewards = pcall(wml.array_access.get, "ap_location_rewards")
        if ok and type(rewards) == "table" then
            for _, reward in ipairs(rewards) do
                if reward.location == name and reward.item and reward.player then
                    return reward.item .. " for " .. reward.player
                end
            end
        end
    end

    local count = wesnoth.get_variable("ap_location_rewards.length") or 0
    for index = 0, count - 1 do
        local prefix = "ap_location_rewards[" .. index .. "]"
        if wesnoth.get_variable(prefix .. ".location") == name then
            local item = wesnoth.get_variable(prefix .. ".item")
            local player = wesnoth.get_variable(prefix .. ".player")
            if item and player then
                return item .. " for " .. player
            end
        end
    end
    return nil
end

function bridge.mark_location(name)
    bridge.load()
    local checked = table_from_variable_array("ap_checked_locations", "name")
    table.insert(checked, name)
    write_variable_array("ap_checked_locations", "name", unique_sorted(checked))
end

local function each_chest(scenario_id, callback)
    if wml and wml.array_access then
        local ok, chests = pcall(wml.array_access.get, "ap_two_brothers_chests")
        if ok and type(chests) == "table" then
            for _, chest in ipairs(chests) do
                if chest.scenario == scenario_id then
                    callback({
                        name = chest.name,
                        x = chest.x,
                        y = chest.y
                    })
                end
            end
            return
        end
    end

    local count = wesnoth.get_variable("ap_two_brothers_chests.length") or 0
    for index = 0, count - 1 do
        local prefix = "ap_two_brothers_chests[" .. index .. "]"
        local scenario = wesnoth.get_variable(prefix .. ".scenario")
        if scenario == scenario_id then
            callback({
                name = wesnoth.get_variable(prefix .. ".name"),
                x = wesnoth.get_variable(prefix .. ".x"),
                y = wesnoth.get_variable(prefix .. ".y")
            })
        end
    end
end

function bridge.place_chests(scenario_id)
    bridge.load()
    each_chest(scenario_id, function(chest)
        if chest.name and chest.x and chest.y and not bridge.is_location_checked(chest.name) then
            wesnoth.wml_actions.item {
                x = chest.x,
                y = chest.y,
                image = "items/chest-plain-closed.png"
            }
        end
    end)
end

function bridge.check_chest_at(scenario_id, x, y)
    bridge.load()
    local checked_name = nil
    local checked_reward = nil
    each_chest(scenario_id, function(chest)
        if checked_name then
            return
        end
        if chest.name and tonumber(chest.x) == tonumber(x) and tonumber(chest.y) == tonumber(y) and not bridge.is_location_checked(chest.name) then
            wesnoth.wml_actions.remove_item {
                x = chest.x,
                y = chest.y,
                image = "items/chest-plain-closed.png"
            }
            wesnoth.wml_actions.item {
                x = chest.x,
                y = chest.y,
                image = "items/chest-plain-open.png"
            }
            checked_reward = bridge.location_reward_text(chest.name)
            bridge.mark_location(chest.name)
            checked_name = chest.name
        end
    end)
    return checked_name, checked_reward or bridge.location_reward_text(checked_name)
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

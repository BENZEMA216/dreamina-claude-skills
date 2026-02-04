# Global Information Planner（全局角色一致性管理）

> 来源: `agents/global_information_planner.py` | 类: `GlobalInformationPlanner` | 方法: `merge_characters_across_scenes_in_event()`, `merge_characters_to_existing_characters_in_novel()`

## 功能说明

管理角色在多场景、多事件间的一致性。包含两个层级的角色合并：(1) 同一事件内跨场景合并，(2) 跨事件合并到小说级别的全局角色列表。确保同一角色在不同场景中使用统一标识。

---

## 功能一：跨场景角色合并（merge_characters_across_scenes_in_event）

### System Prompt

```
You are an expert script analysis and character fusion specialist. Your role is to intelligently analyze multiple script scenes, identify characters that represent the same entity across different scenes, and merge them into a unified character list with consistent identifiers.

**TASK**
Process the input scenes, each containing a script and characters with their names and features. Identify and merge characters that are logically the same across scenes, even if they have different names or slight variations in description. Output a consolidated list of characters for the entire event. Each character in the list must have a unique identifier, along with the scene numbers where they appear and the name used in each scene. You also need to aggregate the static features of the same characters together.

**INPUT**
A sequence of scenes. Each scene is enclosed within <SCENE_N_START> and <SCENE_N_END> tags, where N is the scene number(starting from 0).
Each scene includes a screnplay script and a sequence of character names.
The screenplay script is enclosed within <SCRIPT_START> and <SCRIPT_END> tags.
The sequence of character is enclosed within <CHARACTERS_START> and <CHARACTERS_END> tags. Each character in the list is enclosed within <CHARACTER_M_START> and <CHARACTER_M_END> tags, where M is the character number(starting from 0).

Below is an example of one scene:

<SCENE_0_START>

<SCRIPT_START>
John enters the room and sees Mary.
John: Hi Mary, how are you?
Mary: I'm good, John. Thanks for asking!
<SCRIPT_END>

<CHARACTERS_START>

<CHARACTER_0_START>
John [visible]
static features: John is a tall man with short black hair and brown eyes.
dynamic features: Wearing a blue shirt and black pants.
<CHARACTER_0_END>

<CHARACTER_1_START>
Mary [visible]
static features: Mary is a young woman with long brown hair and green eyes.
dynamic features: Wearing a floral dress and a denim jacket.
<CHARACTER_1_END>

<CHARACTERS_END>

<SCENE_0_END>



**OUTPUT**
{format_instructions}

**GUIDELINES**
1. Character Fusion: Analyze contextual clues (e.g., dialogue style, role in plot, relationships, descriptions) to determine if characters from different scenes are the same person, even if names vary.
2. Unique Identifier: Assign a consistent, unique ID (e.g., primary/canonical name) to each merged character. Use the most frequent or contextually appropriate name as the identifier, if possible.
3. Scene Mapping: For each character, list all scenes they appear in and the exact name used in each scene.
4. Completeness: Ensure all characters from all scenes are included in the final list. No duplicate, omitted, or extraneous characters.
5. If a character undergoes significant changes across different scenes, it is necessary to split them into separate roles. For example, if Character A is a child in Scene 0 but an adult in Scene 1, they should be divided into two distinct characters (meaning two different actors are required to portray them).
6. The language of outputs in values should be same as the input text.
```

### Human Prompt Template

```
{scenes_sequence}
```

> 注：`{scenes_sequence}` 在代码中通过遍历 scenes 构建，包含每个场景的 `<SCENE_N_START>...<SCENE_N_END>` 标签。

### 输出数据结构 — `MergeCharactersAcrossScenesInEventResponse`

| 字段 | 类型 | 说明 |
|------|------|------|
| `characters` | `List[CharacterInEvent]` | 合并后的事件级别角色列表 |

### `CharacterInEvent`

| 字段 | 类型 | 说明 |
|------|------|------|
| `index` | `int` | 角色在事件中的索引 |
| `identifier_in_event` | `str` | 角色在事件中的唯一标识 |
| `active_scenes` | `Dict[int, str]` | 场景索引→场景内角色名的映射 |
| `static_features` | `str` | 聚合后的静态特征 |

---

## 功能二：合并到小说级别（merge_characters_to_existing_characters_in_novel）

### System Prompt

```
You are an information integration expert skilled in accurately identifying, matching, and merging character information. Your responsibility is to ensure consistency in character attributes and efficiently maintain and update the global character list.

**TASK**
Merge the character list extracted from the current event (which may include new or existing characters) into the global character list. For existing characters, ensure their feature descriptions remain consistent; for new characters, add them to the global list.

**INPUT**
1. Existing Characters in the Novel: A list of characters already present in the novel, each with a unique index, identifier, and static features. The list is enclosed within <EXISTING_CHARACTERS_START> and <EXISTING_CHARACTERS_END> tags. Each character in the list is enclosed within <CHARACTER_P_START> and <CHARACTER_P_END> tags, where P is the character number(starting from 0).
2. Characters in the Current Event: A list of characters identified in the current event, each with an index, identifier, active scenes, and static features. The list is enclosed within <EVENT_CHARACTERS_START> and <EVENT_CHARACTERS_END> tags. Each character in the list is enclosed within <CHARACTER_Q_START> and <CHARACTER_Q_END> tags, where Q is the character number(starting from 0).


**OUTPUT**
{format_instructions}

**GUIDELINES**
1. Feature Consistency: Strictly compare the features of the current event characters with those of existing characters. Some character's identifier may be the same as existing role identifier, but their features differ, such as youth and old age. You need to distinguish them as two separate characters.
2. Efficient Merging: Avoid duplicate characters to ensure the list remains concise.
3. Feature Update: If an existing character's features are expanded or modified based on new information from the current event, update their description accordingly.
```

### Human Prompt Template

```
<EXISTING_CHARACTERS_START>
{existing_characters_in_novel}
<EXISTING_CHARACTERS_END>

<EVENT_CHARACTERS_START>
{characters_in_event}
<EVENT_CHARACTERS_END>
```

### 输入变量

| 变量 | 说明 |
|------|------|
| `{existing_characters_in_novel}` | 当前小说级别的全局角色列表 |
| `{characters_in_event}` | 当前事件中提取的角色列表 |

### 输出数据结构 — `MergeCharactersToExistingCharactersInNovelResponse`

| 字段 | 类型 | 说明 |
|------|------|------|
| `characters` | `List[CharacterForMergingToNovel]` | 合并映射列表 |

### `CharacterForMergingToNovel`

| 字段 | 类型 | 说明 |
|------|------|------|
| `index_in_event` | `int` | 角色在事件列表中的索引 |
| `index_in_novel` | `int` | 角色在小说列表中的索引（新角色为 -1） |
| `identifier_in_novel` | `str` | 角色在小说中的唯一标识 |
| `modified_features` | `str` | 合并后的完整静态特征 |

### `CharacterInNovel`（最终全局角色结构）

| 字段 | 类型 | 说明 |
|------|------|------|
| `index` | `int` | 角色在小说中的索引 |
| `identifier_in_novel` | `str` | 唯一标识 |
| `active_events` | `Dict[int, str]` | 事件索引→事件内标识的映射 |
| `static_features` | `str` | 静态特征 |

---

## 使用要点

- **两层合并**：先在事件内跨场景合并（识别同一人），再合并到全局小说角色列表
- **名称变化处理**：即使名称不同，也会通过上下文线索（对话风格、剧情角色、关系）判断是否为同一角色
- **年龄变化分离**：如果同一角色在不同场景中发生显著变化（如童年→成年），应拆分为两个独立角色
- **特征更新**：已存在角色的特征会根据新事件中的信息进行更新和扩展
- **完整性校验**：代码中会验证所有场景角色都被包含在合并结果中，无遗漏
- **index_in_novel = -1**：表示新角色，将被添加到全局列表

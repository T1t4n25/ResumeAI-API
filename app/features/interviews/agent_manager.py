
from dotenv import load_dotenv
from livekit import agents
from livekit.rtc import Room
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    google,
    noise_cancellation,
)
import json
from datetime import datetime
import asyncio
import os

load_dotenv()


class InterviewerHardSkills(Agent):
    def __init__(self, resume, job_description) -> None:
        super().__init__(instructions=f"""

You are an interview agent (Ahmed) conducting a fair and structured technical interview. Follow these principles:
interview structure:
Intro : Setup Welcome, explain flow, ensure comfort
Warm-up : Question Open-ended, non-controversial (e.g., “Tell me about a project you enjoyed”) 
Main Task : A real-world, multi-phase coding/design problem
Follow-up : Explore edge cases, trade-offs, or reflections
Wrap-up : Thank the candidate, explain next steps

talk to the user in the dialect and language he talks to you in
General Conduct
Be supportive and non-adversarial
Avoid judging unrelated traits (e.g. personality, background)
Clearly inform the candidate of what to expect, days in advance

Interview Structure
Use the same core questions across all candidates
Start with open-ended, easy-to-answer questions
Focus on evidence-based answers
If asking for critique (self or company), signal that it's okay

Coding Task Design
Avoid asking for well-known algorithms
Use real-world problems, ideally with multiple phases
Allow the use of their laptop and preferred tools
Test a limited set of skills, not everything at once

Closing
Thank the candidate
Do not begin evaluating during or after the call — evaluation is handled separately

interviewee resume: {resume}
job description: {job_description}
""")


class AgentManager():
    def __init__(self, logger, livekit_manager) -> None:
        self.logger = logger
        self.url = os.getenv("LIVEKIT_URL")
        self.livekit_manager = livekit_manager
        self.active_agents = {}  # Store active agent workers by room name
        
    # it is called when the agent is started
    async def entrypoint(self, context: agents.JobContext):
        session = AgentSession(
            llm=google.beta.realtime.RealtimeModel(
                voice="Puck",
                temperature=0.8,
                max_output_tokens="2000",
                modalities=["AUDIO"],
            )
        )
        # This function will be called when the agent is stopped
        # It writes the transcript of the interview to a file
        async def write_transcript(self):
            current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcript_{context.room.name}_{current_date}.json"
            with open(filename, 'w') as f:
                trans = session.history.to_dict()
                trans["chat"] = trans.pop("items")
                for item in trans["chat"]:  
                    # Remove unwanted fields
                    item.pop("id", None)
                    item.pop("type", None)
                json.dump(trans, f, indent=2)
                
            self.logger.info(f"Transcript for {context.room.name} saved to {filename}")

        context.add_shutdown_callback(write_transcript)
        
        # Start the agent session with the room and input options
        await session.start(
            room=context.room,
            agent=InterviewerHardSkills(),
            room_input_options=RoomInputOptions(
                # LiveKit Cloud enhanced noise cancellation
                noise_cancellation=noise_cancellation.BVC(),
                
            ),
        )

        await context.connect()

        await session.generate_reply(
            instructions="Greet the user and start interview."
        )

    async def start_agent_in_room(self, room_name: str, resume: str, job_description: str):
        """
        Directly connect an agent to a specific room
        This is the most straightforward approach for your use case
        """
        try:
            self.logger.info(f"Starting agent for room: {room_name}")
            
            # Create room connection for the agent
            room = Room()
            
            # Generate token for the agent to join the room
            agent_token = await self.livekit_manager.generate_token(room_name, f"agent-{room_name}")
            
            # Connect agent to the room
            await room.connect(self.url, agent_token)
            
            # Create and start the agent session
            session = AgentSession(
                llm=google.beta.realtime.RealtimeModel(
                    voice="puck",
                    temperature=0.7,
                    max_output_tokens="1000",
                    modalities=["AUDIO"],
                    api_key=os.getenv("GEMINI_API_KEY")
                    #turn_detection=google.beta.realtime.TurnDetection.server_vad(),
                )
            )
            
            # Start the session in the connected room
            async def start_session():
                try:    
                    self.logger.info("starting now")
                    await session.start(
                        room=room,
                        agent=InterviewerHardSkills(resume=resume, job_description=job_description),
                        room_input_options=RoomInputOptions(
                            noise_cancellation=noise_cancellation.BVC(),
                            close_on_disconnect=True,
                        ),
                    )
                except Exception as e:
                    self.logger.error("Session could not start because: " + str(e))
            task = asyncio.create_task(start_session())
            
            await asyncio.sleep(1)
            
            await session.generate_reply(
                instructions="Greet the user start the interview"
            )
            
            self.active_agents[room_name] = {
                'session': session,
                'room': room,
                'task': task
            }
            
            self.logger.info(f"Agent successfully started in room: {room_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start agent in room {room_name}: {e}")
            raise
